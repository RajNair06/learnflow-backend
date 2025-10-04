from django.core.management.base import BaseCommand
from django.test import Client
from django.core.cache import cache
from tabulate import tabulate
import time
import logging

logger=logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Benchmark MonthlySummaryView and WeeklySummaryView with and without caching'

    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=int, default=1, help='User ID for benchmarking')

    def handle(self, *args, **kwargs):
        user_id = kwargs['user_id']
        client = Client()
        urls = {
            'Monthly Summary': f'/api/summary/monthly/1/?user_id={user_id}',
            'Weekly Summary': f'/api/summary/weekly/1/?user_id={user_id}'
        }
        results = []

        for view_name, url in urls.items():
            # Benchmark without cache
            no_cache_times = []
            for i in range(100):
                cache.clear()
                start_time = time.time()
                response = client.get(url)
                end_time = time.time()
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"{view_name} no-cache request {i+1} failed: {response.content}"))
                    return
                no_cache_times.append((end_time - start_time) * 1000)
                self.stdout.write(self.style.SUCCESS(f"{view_name} no-cache request {i+1}: {no_cache_times[-1]:.2f} ms"))

            # Benchmark with cache (pre-populate cache first)
            cache_times = []
            cache.clear()
            response = client.get(url)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"{view_name} cache pre-population failed: {response.content}"))
                return
            for i in range(100):
                start_time = time.time()
                response = client.get(url)
                end_time = time.time()
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f"{view_name} cache request {i+1} failed: {response.content}"))
                    return
                cache_times.append((end_time - start_time) * 1000)
                self.stdout.write(self.style.SUCCESS(f"{view_name} cache request {i+1}: {cache_times[-1]:.2f} ms"))

            results.append([f"{view_name} Without Cache", f"{sum(no_cache_times) / len(no_cache_times):.2f}"])
            results.append([f"{view_name} With Cache", f"{sum(cache_times) / len(cache_times):.2f}"])

        table = [["Scenario", "Average Latency (ms)"]] + results
        self.stdout.write("\nBenchmark Results:")
        self.stdout.write(tabulate(table, headers="firstrow", tablefmt="grid"))