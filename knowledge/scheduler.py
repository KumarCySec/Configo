"""
CONFIGO Knowledge Scheduler
===========================

Scheduler for automatic knowledge graph expansion and maintenance.
Supports cron-like scheduling and on-demand expansion.

Features:
- 🕐 Scheduled knowledge expansion
- 🎯 Domain-specific expansion
- 📊 Progress tracking
- 🔄 Automatic retry logic
- 📈 Growth metrics
"""

import os
import logging
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    """Represents a scheduled knowledge expansion task."""
    task_id: str
    domain: str
    schedule: str  # cron-like schedule or "daily", "weekly"
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    total_runtime: float = 0.0
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ExpansionResult:
    """Represents the result of a knowledge expansion operation."""
    task_id: str
    domain: str
    success: bool
    start_time: datetime
    end_time: datetime
    nodes_added: int = 0
    relationships_added: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class KnowledgeScheduler:
    """
    Scheduler for automatic knowledge graph expansion.
    
    Manages scheduled tasks and provides on-demand expansion capabilities.
    """
    
    def __init__(self, knowledge_engine, storage_path: str = ".configo_scheduler"):
        """
        Initialize the knowledge scheduler.
        
        Args:
            knowledge_engine: Knowledge engine instance
            storage_path: Path for storing scheduler data
        """
        self.knowledge_engine = knowledge_engine
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Task management
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.expansion_history: List[ExpansionResult] = []
        self.is_running = False
        self.scheduler_thread = None
        
        # Load existing tasks
        self._load_tasks()
        
        logger.info("Knowledge scheduler initialized")
    
    def add_scheduled_task(self, domain: str, schedule: str = "daily") -> str:
        """
        Add a scheduled task for knowledge expansion.
        
        Args:
            domain: Domain to expand (e.g., "ai stack", "devops essentials")
            schedule: Schedule string ("daily", "weekly", or cron-like)
            
        Returns:
            str: Task ID
        """
        task_id = f"task_{domain.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = ScheduledTask(
            task_id=task_id,
            domain=domain,
            schedule=schedule,
            next_run=self._calculate_next_run(schedule)
        )
        
        self.scheduled_tasks[task_id] = task
        self._save_tasks()
        
        logger.info(f"Added scheduled task: {task_id} for domain: {domain}")
        return task_id
    
    def remove_scheduled_task(self, task_id: str) -> bool:
        """
        Remove a scheduled task.
        
        Args:
            task_id: Task ID to remove
            
        Returns:
            bool: True if successful
        """
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            self._save_tasks()
            logger.info(f"Removed scheduled task: {task_id}")
            return True
        return False
    
    def start_scheduler(self) -> None:
        """Start the scheduler in a background thread."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Knowledge scheduler started")
    
    def stop_scheduler(self) -> None:
        """Stop the scheduler."""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Knowledge scheduler stopped")
    
    def expand_knowledge_now(self, domain: str) -> ExpansionResult:
        """
        Expand knowledge for a domain immediately.
        
        Args:
            domain: Domain to expand
            
        Returns:
            ExpansionResult: Result of the expansion
        """
        task_id = f"manual_{domain.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = ExpansionResult(
            task_id=task_id,
            domain=domain,
            success=False,
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        
        try:
            # Get initial graph statistics
            initial_stats = self.knowledge_engine.get_graph_statistics()
            initial_nodes = initial_stats.get('total_nodes', 0)
            initial_relationships = initial_stats.get('total_relationships', 0)
            
            # Perform expansion
            success = self.knowledge_engine.expand_graph_from_gemini(domain)
            
            # Get final statistics
            final_stats = self.knowledge_engine.get_graph_statistics()
            final_nodes = final_stats.get('total_nodes', 0)
            final_relationships = final_stats.get('total_relationships', 0)
            
            result.success = success
            result.end_time = datetime.now()
            result.nodes_added = final_nodes - initial_nodes
            result.relationships_added = final_relationships - initial_relationships
            result.metadata = {
                'initial_nodes': initial_nodes,
                'final_nodes': final_nodes,
                'initial_relationships': initial_relationships,
                'final_relationships': final_relationships
            }
            
            if not success:
                result.error_message = f"Failed to expand knowledge for domain: {domain}"
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Error during knowledge expansion: {e}")
        
        # Store result
        self.expansion_history.append(result)
        self._save_history()
        
        return result
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get list of scheduled tasks."""
        return [asdict(task) for task in self.scheduled_tasks.values()]
    
    def get_expansion_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get expansion history."""
        return [asdict(result) for result in self.expansion_history[-limit:]]
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        total_tasks = len(self.scheduled_tasks)
        active_tasks = len([t for t in self.scheduled_tasks.values() if t.is_active])
        
        recent_results = [r for r in self.expansion_history 
                         if r.end_time > datetime.now() - timedelta(days=7)]
        
        success_count = len([r for r in recent_results if r.success])
        failure_count = len([r for r in recent_results if not r.success])
        
        total_nodes_added = sum(r.nodes_added for r in recent_results)
        total_relationships_added = sum(r.relationships_added for r in recent_results)
        
        return {
            'total_tasks': total_tasks,
            'active_tasks': active_tasks,
            'recent_expansions': len(recent_results),
            'recent_successes': success_count,
            'recent_failures': failure_count,
            'total_nodes_added': total_nodes_added,
            'total_relationships_added': total_relationships_added,
            'is_running': self.is_running
        }
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.is_running:
            try:
                now = datetime.now()
                
                # Check for tasks that need to run
                for task in self.scheduled_tasks.values():
                    if not task.is_active:
                        continue
                    
                    if task.next_run and now >= task.next_run:
                        # Execute task
                        result = self.expand_knowledge_now(task.domain)
                        
                        # Update task statistics
                        task.last_run = now
                        task.next_run = self._calculate_next_run(task.schedule)
                        
                        if result.success:
                            task.success_count += 1
                        else:
                            task.failure_count += 1
                        
                        task.total_runtime += (result.end_time - result.start_time).total_seconds()
                        
                        # Save updated tasks
                        self._save_tasks()
                        
                        logger.info(f"Executed scheduled task: {task.task_id} for domain: {task.domain}")
                
                # Sleep for a minute before next check
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time based on schedule."""
        now = datetime.now()
        
        if schedule == "daily":
            return now + timedelta(days=1)
        elif schedule == "weekly":
            return now + timedelta(weeks=1)
        elif schedule == "monthly":
            # Simple monthly calculation
            if now.month == 12:
                return now.replace(year=now.year + 1, month=1)
            else:
                return now.replace(month=now.month + 1)
        else:
            # Default to daily
            return now + timedelta(days=1)
    
    def _load_tasks(self) -> None:
        """Load scheduled tasks from storage."""
        tasks_file = self.storage_path / "scheduled_tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r') as f:
                    tasks_data = json.load(f)
                
                for task_data in tasks_data:
                    task = ScheduledTask(**task_data)
                    # Convert string timestamps back to datetime
                    for field in ['last_run', 'next_run', 'created_at']:
                        if task_data.get(field):
                            setattr(task, field, datetime.fromisoformat(task_data[field]))
                    
                    self.scheduled_tasks[task.task_id] = task
                
                logger.info(f"Loaded {len(self.scheduled_tasks)} scheduled tasks")
            except Exception as e:
                logger.error(f"Failed to load scheduled tasks: {e}")
    
    def _save_tasks(self) -> None:
        """Save scheduled tasks to storage."""
        tasks_file = self.storage_path / "scheduled_tasks.json"
        try:
            tasks_data = []
            for task in self.scheduled_tasks.values():
                task_dict = asdict(task)
                # Convert datetime objects to ISO strings
                for field in ['last_run', 'next_run', 'created_at']:
                    if task_dict.get(field):
                        task_dict[field] = task_dict[field].isoformat()
                tasks_data.append(task_dict)
            
            with open(tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save scheduled tasks: {e}")
    
    def _save_history(self) -> None:
        """Save expansion history to storage."""
        history_file = self.storage_path / "expansion_history.json"
        try:
            # Keep only last 1000 results to prevent file from growing too large
            recent_history = self.expansion_history[-1000:]
            
            history_data = []
            for result in recent_history:
                result_dict = asdict(result)
                # Convert datetime objects to ISO strings
                for field in ['start_time', 'end_time']:
                    if result_dict.get(field):
                        result_dict[field] = result_dict[field].isoformat()
                history_data.append(result_dict)
            
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save expansion history: {e}")
    
    def _load_history(self) -> None:
        """Load expansion history from storage."""
        history_file = self.storage_path / "expansion_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                
                for result_data in history_data:
                    result = ExpansionResult(**result_data)
                    # Convert string timestamps back to datetime
                    for field in ['start_time', 'end_time']:
                        if result_data.get(field):
                            setattr(result, field, datetime.fromisoformat(result_data[field]))
                    
                    self.expansion_history.append(result)
                
                logger.info(f"Loaded {len(self.expansion_history)} expansion history records")
            except Exception as e:
                logger.error(f"Failed to load expansion history: {e}") 