import os
import asyncio
import logging
import concurrent.futures
from .config import Config

logger = logging.getLogger(__name__)

class ProcessManager:
    """Manages FFmpeg processes and system resources"""
    
    def __init__(self):
        self.max_processes = Config.FFMPEG_PROCESSES
        self.current_processes = 0
        self.lock = asyncio.Lock()
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_processes
        )
    
    async def adjust_processes(self) -> None:
        """Dynamically adjust process count based on system load"""
        async with self.lock:
            try:
                # Get system load average (Unix-like systems only)
                load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 1.0
            except:
                load = 1.0
            
            # Adjust based on load
            if load > 2.0 and self.max_processes > 2:
                new_max = max(2, self.max_processes - 1)
                logger.info(f"High load detected. Reducing processes: {self.max_processes} -> {new_max}")
                self.max_processes = new_max
            elif load < 1.0 and self.max_processes < Config.FFMPEG_PROCESSES:
                new_max = min(Config.FFMPEG_PROCESSES, self.max_processes + 1)
                logger.info(f"Low load detected. Increasing processes: {self.max_processes} -> {new_max}")
                self.max_processes = new_max
            
            # Update executor if needed
            if self.executor._max_workers != self.max_processes:
                self.executor._max_workers = self.max_processes
    
    async def get_executor(self) -> concurrent.futures.ThreadPoolExecutor:
        """Get the thread pool executor"""
        await self.adjust_processes()
        return self.executor
    
    def get_ffmpeg_options(self, chat_id: int, is_video: bool = False) -> dict:
        """Get optimized FFmpeg options"""
        base_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn' if not is_video else ''
        }
        
        # Adjust buffer size based on chat type
        if chat_id < 0:  # Group chat
            base_options['options'] += ' -bufsize 1024k'
        else:  # Private chat
            base_options['options'] += ' -bufsize 512k'
        
        # Set thread count
        base_options['options'] += f' -threads {min(self.max_processes, 8)}'
        
        return base_options
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)
            logger.info("Process manager cleaned up")

# Global process manager instance
process_manager = ProcessManager()