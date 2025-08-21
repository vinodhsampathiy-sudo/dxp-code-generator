from typing import Dict, List, Any, Coroutine, Optional
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)

class ParallelProcessor:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_groups: Dict[str, List[Coroutine]] = {
            'sling': [],  # Sling Model tasks
            'htl': [],    # HTL generation tasks
            'dialog': [], # Dialog XML tasks
            'clientlib': [], # Client library tasks
            'validation': [], # Validation tasks
            'io': []      # File I/O tasks
        }
        self.results: Dict[str, Any] = {}
        self.timing: Dict[str, float] = {}

    async def add_task(self, group: str, coro: Coroutine, task_id: Optional[str] = None):
        """Add a task to a specific group"""
        if group not in self.task_groups:
            raise ValueError(f"Invalid task group: {group}")
        self.task_groups[group].append(coro)
        if task_id:
            self.results[task_id] = None

    async def process_group(self, group: str) -> List[Any]:
        """Process all tasks in a specific group"""
        if not self.task_groups[group]:
            return []

        start_time = time.time()
        try:
            results = await asyncio.gather(*self.task_groups[group], return_exceptions=True)
            self.timing[group] = time.time() - start_time
            return results
        except Exception as e:
            logger.error(f"Error processing task group {group}: {str(e)}")
            raise

    async def process_independent_groups(self) -> Dict[str, List[Any]]:
        """Process groups that can run in parallel"""
        independent_groups = {
            'component_generation': ['htl', 'dialog'],
            'assets': ['clientlib'],
            'validation': ['validation']
        }

        results = {}
        for group_name, groups in independent_groups.items():
            tasks = []
            for g in groups:
                tasks.extend(self.task_groups.get(g, []))
            if tasks:
                start_time = time.time()
                group_results = await asyncio.gather(*tasks, return_exceptions=True)
                self.timing[group_name] = time.time() - start_time
                results[group_name] = group_results

        return results

    async def process_sequential_groups(self, order: List[str]) -> Dict[str, List[Any]]:
        """Process groups that must run in sequence"""
        results = {}
        for group in order:
            if self.task_groups.get(group):
                results[group] = await self.process_group(group)
        return results

    def get_timing_report(self) -> Dict[str, Any]:
        """Get timing statistics for processed tasks"""
        total_time = sum(self.timing.values())
        return {
            'total_time': total_time,
            'group_timing': self.timing,
            'percentage': {
                group: (time / total_time) * 100 
                for group, time in self.timing.items()
            }
        }

    @staticmethod
    async def chunk_tasks(tasks: List[Coroutine], chunk_size: int) -> List[List[Coroutine]]:
        """Split tasks into smaller chunks for better parallelization"""
        return [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]

    async def process_with_rate_limit(
        self,
        tasks: List[Coroutine],
        rate_limit: int,
        chunk_size: Optional[int] = None
    ) -> List[Any]:
        """Process tasks with rate limiting to prevent overload"""
        if chunk_size:
            chunks = await self.chunk_tasks(tasks, chunk_size)
        else:
            chunks = [[task] for task in tasks]

        results = []
        semaphore = asyncio.Semaphore(rate_limit)

        async def process_with_semaphore(chunk):
            async with semaphore:
                chunk_results = await asyncio.gather(*chunk, return_exceptions=True)
                results.extend(chunk_results)
                await asyncio.sleep(0.1)  # Prevent tight loop

        await asyncio.gather(
            *[process_with_semaphore(chunk) for chunk in chunks]
        )

        return results
