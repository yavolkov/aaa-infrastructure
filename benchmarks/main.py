import time
import requests


text = """Перед замером необходимо выбрать метрики, которые потенциально важно знать
для реализованного инференс-сервиса.

Метрики вы выбираете самостоятельно, выбор метрик нужно обосновать в отчёте.

Возможные кандидаты (подумайте, какие из них важны именно для inference service и почему):"""
n_words = len(text.split())


def measure_latency(url, n_requests=1000):
    latencies = []

    for _ in range(n_requests):
        start_time = time.time()
        response = requests.post(url, json={"text": text})
        end_time = time.time()

        if response.status_code != 200:
            raise Exception("Request failed")

        latency = end_time - start_time
        latencies.append(latency)

    latencies.sort()
    mn = sum(latencies) / len(latencies)
    p50 = latencies[int(0.50 * len(latencies))]
    p95 = latencies[int(0.95 * len(latencies))]
    p99 = latencies[int(0.99 * len(latencies))]

    return mn, p50, p95, p99


def measure_rps(url, n_requests=1000):
    start_time = time.time()

    for _ in range(n_requests):
        response = requests.post(url, json={"text": text})
        if response.status_code != 200:
            raise Exception("Request failed")

    end_time = time.time()
    total_time = end_time - start_time
    rps = n_requests / total_time
    wps = n_requests * n_words / total_time
    return total_time, rps, wps


mn, p50, p95, p99 = measure_latency('http://localhost:8080/embed')
total_time, rps, wps = measure_rps("http://localhost:8080/embed")
print("====Latencies====")
print(f"Mean: {mn}, P50: {p50} sec, P95: {p95} sec, P99: {p99} sec")
print(f"total_time: {total_time} sec, RPS: {rps}, WPS: {wps}")
