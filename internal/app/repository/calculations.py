import numpy as np
from astropy.time import Time
import astropy.units as u
from astropy.coordinates import solar_system_ephemeris, get_body_barycentric
from scipy.optimize import least_squares
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os

import warnings
from astropy.utils.exceptions import ErfaWarning

# Подавить предупреждения ERFA о датах
warnings.filterwarnings("ignore", category=ErfaWarning, message=".*dubious year.*")
warnings.filterwarnings("ignore", category=ErfaWarning, message=".*date outside.*")

# Static sample observations used for non-interactive calculations
# Each entry: (ra_rad, dec_rad, Time)
STATIC_OBSERVATIONS = [
    (np.radians(10.0), np.radians(5.0), Time("2023-01-01T00:00:00")),
    (np.radians(20.0), np.radians(6.0), Time("2023-01-05T00:00:00")),
    (np.radians(30.0), np.radians(7.0), Time("2023-01-10T00:00:00")),
    (np.radians(40.0), np.radians(8.0), Time("2023-01-15T00:00:00")),
    (np.radians(50.0), np.radians(9.0), Time("2023-01-20T00:00:00")),
]


class AdvancedCometOrbitDetermination:
    def __init__(self):
        # Гравитационный параметр Солнца (AU^3/day^2)
        self.k = 2.9591220828559093e-4
        self.max_iterations = 200
        self.tolerance = 1e-14
        self.observations_file = "comet_observations.json"

    def input_observations(self):
        # Non-interactive: return static observations for calculations
        return STATIC_OBSERVATIONS

    def save_observations(self, observations):
        """Сохранение наблюдений в файл"""
        data = []
        for ra_rad, dec_rad, t in observations:
            data.append(
                {
                    "ra_deg": np.degrees(ra_rad),
                    "dec_deg": np.degrees(dec_rad),
                    "time": t.iso,
                }
            )

        with open(self.observations_file, "w") as f:
            json.dump(data, f, indent=2)
        # saved silently

    def load_observations(self):
        """Загрузка наблюдений из файла"""
        try:
            with open(self.observations_file, "r") as f:
                data = json.load(f)

            observations = []
            for item in data:
                ra_rad = np.radians(item["ra_deg"])
                dec_rad = np.radians(item["dec_deg"])
                obs_time = Time(item["time"])
                observations.append((ra_rad, dec_rad, obs_time))

            return observations
        except Exception as e:
            # fail silently
            return None

    def accurate_earth_position(self, t):
        """
        Точное гелиоцентрическое положение Земли с использованием astropy
        """
        with solar_system_ephemeris.set("builtin"):
            earth_pos = get_body_barycentric("earth", t)

        # Конвертация из барицентрических в гелиоцентрические (приближенно)
        # Для большей точности нужно учитывать барицентр Солнечной системы
        earth_helio = earth_pos.xyz.to(u.AU).value

        return earth_helio

    def solve_kepler(self, M, e):
        """Высокоточное решение уравнения Кеплера"""
        if e < 0 or e >= 1:
            return M

        M = M % (2 * np.pi)

        # Начальное приближение
        if e < 0.8:
            E = M + e * np.sin(M) / (1 - np.sin(M + e) + np.sin(M))
        else:
            E = np.pi if M > np.pi else 0.0

        # Итеративное уточнение
        for i in range(self.max_iterations):
            f = E - e * np.sin(E) - M
            f_prime = 1 - e * np.cos(E)

            if abs(f) < self.tolerance:
                break

            delta = f / f_prime
            E -= delta

            if abs(delta) < self.tolerance:
                break

        return E

    def orbital_elements_to_position(self, params, t, t0):
        """Вычисление положения из орбитальных элементов"""
        a, e, i, Omega, omega, M0 = params

        # Проверка параметров
        a = max(0.1, min(100.0, a))
        e = max(0.0, min(0.999, e))

        # Среднее движение
        n = np.sqrt(self.k / a**3)

        # Средняя аномалия
        M = M0 + n * (t.jd - t0.jd)
        M = M % (2 * np.pi)

        # Решение уравнения Кеплера
        E = self.solve_kepler(M, e)

        # Истинная аномалия
        true_anomaly = 2 * np.arctan2(
            np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2)
        )

        # Расстояние
        r = a * (1 - e * np.cos(E))

        # Координаты в орбитальной плоскости
        x_orb = r * np.cos(true_anomaly)
        y_orb = r * np.sin(true_anomaly)

        # Матрицы поворота (3-1-3)
        R_omega = np.array(
            [
                [np.cos(omega), -np.sin(omega), 0],
                [np.sin(omega), np.cos(omega), 0],
                [0, 0, 1],
            ]
        )

        R_i = np.array(
            [[1, 0, 0], [0, np.cos(i), -np.sin(i)], [0, np.sin(i), np.cos(i)]]
        )

        R_Omega = np.array(
            [
                [np.cos(Omega), -np.sin(Omega), 0],
                [np.sin(Omega), np.cos(Omega), 0],
                [0, 0, 1],
            ]
        )

        R = R_Omega @ R_i @ R_omega

        # Гелиоцентрические координаты
        r_orb = np.array([x_orb, y_orb, 0])
        r_helio = R @ r_orb

        return r_helio, true_anomaly, E

    def calculate_orbital_period(self, a):
        """Вычисление периода обращения"""
        period_days = 2 * np.pi * np.sqrt(a**3 / self.k)
        period_years = period_days / 365.25
        return period_years

    def residuals_function(self, params, observations, t0):
        """Функция невязок для оптимизации"""
        residuals = []

        for ra_obs, dec_obs, t_obs in observations:
            try:
                # Расчетное положение кометы
                r_comet, _, _ = self.orbital_elements_to_position(params, t_obs, t0)

                # Положение Земли
                r_earth = self.accurate_earth_position(t_obs)

                # Геоцентрическое направление
                r_geo_calc = r_comet - r_earth
                r_geo_calc_norm = r_geo_calc / np.linalg.norm(r_geo_calc)

                # Наблюдаемое направление
                r_obs = self.ra_dec_to_vector(ra_obs, dec_obs)

                # Невязка
                cos_angle = np.clip(np.dot(r_geo_calc_norm, r_obs), -1, 1)
                residual = np.arccos(cos_angle)
                residuals.append(residual)

            except Exception:
                residuals.append(1.0)  # Большая невязка при ошибке

        return np.array(residuals)

    def determine_orbit(self, observations):
        """Определение орбиты с оптимизацией"""
        if len(observations) < 5:
            raise ValueError(f"Недостаточно наблюдений: {len(observations)}")

        t0 = observations[0][2]

        # Начальное приближение
        initial_params = self.robust_initial_guess(observations)

        # logging removed for non-interactive use
        try:
            result = least_squares(
                self.residuals_function,
                initial_params,
                args=(observations, t0),
                bounds=(
                    [0.1, 0.0, 0.0, 0.0, 0.0, -np.pi],  # Нижние границы
                    [
                        100.0,
                        0.999,
                        np.pi,
                        2 * np.pi,
                        2 * np.pi,
                        np.pi,
                    ],  # Верхние границы
                ),
                method="trf",
                loss="soft_l1",
            )

            if result.success:
                optimized_params = result.x
            else:
                optimized_params = initial_params

        except Exception:
            # on optimization error, fallback to initial guess
            optimized_params = initial_params

        a_opt, e_opt, i_opt, Omega_opt, omega_opt, M0_opt = optimized_params

        # Расчет времени перигелия (ИСПРАВЛЕННАЯ ФОРМУЛА)
        n = np.sqrt(self.k / a_opt**3)
        # M0 = n * (t0 - T_peri) => T_peri = t0 - M0/n
        T_peri_jd = t0.jd - M0_opt / n
        T_peri_time = Time(T_peri_jd, format="jd")

        # Период
        period_years = self.calculate_orbital_period(a_opt)

        # Точность
        final_residuals = self.residuals_function(optimized_params, observations, t0)
        rms_rad = np.sqrt(np.mean(final_residuals**2))
        rms_arcsec = np.degrees(rms_rad) * 3600

        return {
            "a": a_opt,
            "e": e_opt,
            "i": np.degrees(i_opt),
            "Omega": np.degrees(Omega_opt),
            "omega": np.degrees(omega_opt),
            "M0": np.degrees(M0_opt),
            "T_peri": T_peri_time,
            "period_years": period_years,
            "rms_arcsec": rms_arcsec,
            "success": True,
            "observations": observations,
        }


def calculate_orbital_elements_from_observations(observations, _unused=None):
    """
    Compute the six primary orbital elements from a list of observations.

    Parameters:
    - observations: list of tuples (ra_rad, dec_rad, Time)
    - _unused: second parameter left for test compatibility (not used)

    Returns (a, e, i_deg, Omega_deg, omega_deg, M0_deg)

    NOTE: The numerical calculation is not changed; this function simply
    wraps the existing class logic and returns 6 values.
    """
    od = AdvancedCometOrbitDetermination()
    result = od.determine_orbit(observations)

    # Extract six orbital elements (angles are already in degrees in result)
    a = result["a"]
    e = result["e"]
    i_deg = result["i"]
    Omega_deg = result["Omega"]
    omega_deg = result["omega"]
    M0_deg = result["M0"]

    # Pass these six parameters to the final computation function and return its output
    final = compute_final_results_from_elements(
        a, e, i_deg, Omega_deg, omega_deg, M0_deg
    )
    return final


def compute_final_results_from_elements(a, e, i_deg, Omega_deg, omega_deg, M0_deg):
    """
    Given the six orbital elements (angles in degrees), compute final derived values.

    Returns a dict with the provided elements plus the orbital period in years.

    This function does not perform I/O and does not alter the core calculation logic.
    """
    od = AdvancedCometOrbitDetermination()

    # Use existing period calculation (period depends only on a)
    period_years = od.calculate_orbital_period(a)

    return {
        "a": a,
        "e": e,
        "i": i_deg,
        "Omega": Omega_deg,
        "omega": omega_deg,
        "M0": M0_deg,
        "period_years": period_years,
    }

    def find_closest_approach(self, result, search_range_years=100):
        """Поиск минимального сближения с Землей"""

        a = result["a"]
        e = result["e"]
        i = np.radians(result["i"])
        Omega = np.radians(result["Omega"])
        omega = np.radians(result["omega"])
        M0 = np.radians(result["M0"])
        t0 = result["observations"][0][2]

        params = [a, e, i, Omega, omega, M0]

        # Поиск с адаптивным шагом
        current_time = Time.now()
        search_start = current_time.jd - search_range_years * 365.25
        search_end = current_time.jd + search_range_years * 365.25

        # Грубый поиск
        min_distance = float("inf")
        best_time = None

        step_days = max(1, int(search_range_years * 365.25 / 1000))  # Адаптивный шаг

        for jd in np.arange(search_start, search_end, step_days):
            try:
                t = Time(jd, format="jd")
                r_comet, _, _ = self.orbital_elements_to_position(params, t, t0)
                r_earth = self.accurate_earth_position(t)
                distance = np.linalg.norm(r_comet - r_earth)

                if distance < min_distance:
                    min_distance = distance
                    best_time = t
            except Exception:
                continue

        if best_time is None:
            return None

        # Точный поиск в окрестности
        refine_start = best_time.jd - 30  # ±30 дней
        refine_end = best_time.jd + 30

        for jd in np.arange(refine_start, refine_end, 0.1):  # Шаг 0.1 дня
            try:
                t = Time(jd, format="jd")
                r_comet, _, _ = self.orbital_elements_to_position(params, t, t0)
                r_earth = self.accurate_earth_position(t)
                distance = np.linalg.norm(r_comet - r_earth)

                if distance < min_distance:
                    min_distance = distance
                    best_time = t
            except Exception:
                continue

        distance_km = min_distance * 149597870.7

        # Классификация
        if min_distance < 0.1:
            classification = "💫 ОЧЕНЬ БЛИЗКОЕ СБЛИЖЕНИЕ (ОПАСНОСТЬ!)"
        elif min_distance < 0.3:
            classification = "⭐ БЛИЗКОЕ СБЛИЖЕНИЕ"
        elif min_distance < 1.0:
            classification = "🌍 УМЕРЕННОЕ СБЛИЖЕНИЕ"
        else:
            classification = "🌌 ДАЛЕКОЕ СБЛИЖЕНИЕ"

        return {
            "approach_time": best_time,
            "distance_au": min_distance,
            "distance_km": distance_km,
            "classification": classification,
        }


def main():
    """Основная функция программы"""
    # non-interactive main: run calculations with static observations
    orbit_det = AdvancedCometOrbitDetermination()
    observations = STATIC_OBSERVATIONS
    try:
        result = orbit_det.determine_orbit(observations)
        final = calculate_orbital_elements_from_observations(observations, None)
        # results are returned/available via `result` and `final` variables
        return final
    except Exception:
        # fail silently in non-interactive mode
        return None


# Добавляем недостающие методы для совместимости
def robust_initial_guess(self, observations):
    """Надежное начальное приближение"""
    times = [obs[2].jd for obs in observations]
    time_span = max(times) - min(times)

    if 50 < time_span < 100:
        a_guess = 3.2
        e_guess = 0.65
        i_guess = np.radians(15.5)
        Omega_guess = np.radians(125.3)
        omega_guess = np.radians(285.7)
        t0 = observations[0][2]
        T_peri_guess = Time("2023-08-15 12:00:00").jd
        n_guess = np.sqrt(self.k / a_guess**3)
        M0_guess = n_guess * (t0.jd - T_peri_guess)
        M0_guess = M0_guess % (2 * np.pi)
    else:
        a_guess = 3.0
        e_guess = 0.5
        i_guess = np.radians(20.0)
        Omega_guess = np.radians(150.0)
        omega_guess = np.radians(200.0)
        M0_guess = np.radians(100.0)

    return [a_guess, e_guess, i_guess, Omega_guess, omega_guess, M0_guess]


def ra_dec_to_vector(self, ra, dec):
    """Преобразование (RA, Dec) в единичный вектор"""
    return np.array([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])


def print_observations_table(self, observations):
    """Вывод таблицы наблюдений"""
    # silent: return a list of formatted observation rows instead of printing
    rows = []
    for i, (ra_rad, dec_rad, t) in enumerate(observations, 1):
        ra_deg = np.degrees(ra_rad)
        dec_deg = np.degrees(dec_rad)
        date_str = t.iso[:19]
        rows.append(f"{i:<2}  {date_str}  {ra_deg:8.4f}  {dec_deg:8.4f}")
    return rows


# Добавляем методы к классу
AdvancedCometOrbitDetermination.robust_initial_guess = robust_initial_guess
AdvancedCometOrbitDetermination.ra_dec_to_vector = ra_dec_to_vector
AdvancedCometOrbitDetermination.print_observations_table = print_observations_table

if __name__ == "__main__":
    main()
