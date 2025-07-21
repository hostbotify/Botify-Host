import asyncio
import logging
from datetime import datetime
from typing import Set
from .bot import app, tgcaller
from .database import db
from .connection import connection_manager
from .playback import playback_manager
from .config import Config

logger = logging.getLogger(__name__)

class TroubleshootManager:
    """Handles bot troubleshooting and self-repair"""
    
    def __init__(self):
        self.active_repairs: Set[int] = set()
    
    async def log_action(self, chat_id: int, action: str, status: str, details: str = ""):
        """Log troubleshooting action"""
        await db.troubleshooting_logs.insert_one({
            "chat_id": chat_id,
            "action": action,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow()
        })
    
    async def fix_voice_connection(self, chat_id: int) -> bool:
        """Fix voice connection issues"""
        if chat_id in self.active_repairs:
            return False
        
        self.active_repairs.add(chat_id)
        
        try:
            await self.log_action(chat_id, "voice_fix", "started")
            
            # Leave and rejoin voice chat
            await connection_manager.release_connection(chat_id)
            await asyncio.sleep(2)
            
            if not await connection_manager.get_connection(chat_id):
                raise Exception("Failed to establish new connection")
            
            # Resume playback if there was a current track
            if playback_manager.is_playing(chat_id):
                current_track = playback_manager.get_current_track(chat_id)
                if current_track:
                    await playback_manager.play_track(chat_id, current_track, same_track=True)
            
            await self.log_action(chat_id, "voice_fix", "success")
            await app.send_message(chat_id, "✅ Voice connection successfully repaired")
            return True
            
        except Exception as e:
            logger.error(f"Voice fix error in {chat_id}: {e}")
            await self.log_action(chat_id, "voice_fix", "failed", str(e))
            await self.notify_failure(chat_id, str(e))
            return False
        finally:
            self.active_repairs.discard(chat_id)
    
    async def restart_playback(self, chat_id: int) -> bool:
        """Restart current playback"""
        if chat_id in self.active_repairs:
            return False
        
        self.active_repairs.add(chat_id)
        
        try:
            await self.log_action(chat_id, "playback_restart", "started")
            
            if playback_manager.is_playing(chat_id):
                current_track = playback_manager.get_current_track(chat_id)
                if current_track:
                    await playback_manager.play_track(chat_id, current_track, same_track=True)
                    await self.log_action(chat_id, "playback_restart", "success")
                    await app.send_message(chat_id, "✅ Playback successfully restarted")
                    return True
            
            await self.log_action(chat_id, "playback_restart", "failed", "No current stream")
            await app.send_message(chat_id, "❌ No active playback to restart")
            return False
            
        except Exception as e:
            logger.error(f"Playback restart error in {chat_id}: {e}")
            await self.log_action(chat_id, "playback_restart", "failed", str(e))
            await self.notify_failure(chat_id, str(e))
            return False
        finally:
            self.active_repairs.discard(chat_id)
    
    async def check_permissions(self, chat_id: int) -> dict:
        """Check bot permissions in chat"""
        required_perms = {
            "can_manage_voice_chats": "Manage Voice Chats",
            "can_delete_messages": "Delete Messages",
            "can_invite_users": "Invite Users"
        }
        
        try:
            me = await app.get_chat_member(chat_id, "me")
            missing_perms = []
            
            for perm, name in required_perms.items():
                if not getattr(me, perm, False):
                    missing_perms.append(name)
            
            return {
                "status": "success" if not missing_perms else "missing_perms",
                "missing": missing_perms
            }
            
        except Exception as e:
            logger.error(f"Permission check error in {chat_id}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_diagnostics(self, chat_id: int) -> str:
        """Run comprehensive diagnostics"""
        report = ["🔍 **Diagnostic Report**\n"]
        
        # Voice connection status
        conn_status = "✅ Connected" if connection_manager.is_connected(chat_id) else "❌ Disconnected"
        report.append(f"**Voice Connection**: {conn_status}")
        
        # Playback status
        playback_status = "✅ Playing" if playback_manager.is_playing(chat_id) else "❌ Stopped"
        report.append(f"**Playback Status**: {playback_status}")
        
        # Permission check
        perm_result = await self.check_permissions(chat_id)
        if perm_result["status"] == "success":
            report.append("**Permissions**: ✅ All required permissions available")
        elif perm_result["status"] == "missing_perms":
            report.append(f"**Permissions**: ❌ Missing: {', '.join(perm_result['missing'])}")
        else:
            report.append(f"**Permissions**: ❓ Check failed: {perm_result['error']}")
        
        # Queue status
        from .queue import queue_manager
        queue_size = queue_manager.get_queue_size(chat_id)
        report.append(f"**Queue**: {queue_size} tracks")
        
        # Suggested actions
        if "❌" in "\n".join(report):
            report.append("\n**Suggested Action**: Use /fixbot command")
        else:
            report.append("\n**Status**: All systems operational")
        
        return "\n".join(report)
    
    async def notify_failure(self, chat_id: int, error: str):
        """Notify about repair failure"""
        error_msg = (
            f"❌ **Automatic repair failed**\n\n"
            f"**Error**: {error[:200]}\n\n"
            f"Please contact @{Config.SUPER_GROUP_USERNAME} for assistance"
        )
        
        try:
            await app.send_message(chat_id, error_msg)
        except Exception as e:
            logger.error(f"Failed to send failure notification to {chat_id}: {e}")
        
        # Notify super group
        await app.send_message(
            Config.SUPER_GROUP_ID,
            f"🚨 **Repair Failed**\n"
            f"**Chat ID**: {chat_id}\n"
            f"**Error**: {error}\n\n"
            f"Manual intervention required"
        )
    
    async def health_check_all_chats(self):
        """Check health of all active chats"""
        if not db.enabled:
            logger.debug("Database not enabled. Skipping health check.")
            return
            
        try:
            all_chats = await db.chats.find().to_list(None)
            for chat in all_chats:
                chat_id = chat["chat_id"]
                
                # Skip if already being repaired
                if chat_id in self.active_repairs:
                    continue
                
                try:
                    # Check if bot is alone in voice chat
                    if connection_manager.is_connected(chat_id):
                        # Check if call is still active using TgCaller
                        call_info = await tgcaller.get_call(chat_id)
                        if not call_info:
                            await self.log_action(
                                chat_id,
                                "health_check",
                                "disconnected",
                                "Call disconnected"
                            )
                            await connection_manager.release_connection(chat_id)
                            
                except Exception as e:
                    logger.error(f"Health check error for {chat_id}: {e}")
                    await self.log_action(
                        chat_id,
                        "health_check",
                        "failed",
                        str(e)
                    )
        except Exception as e:
            logger.error(f"Global health check error: {e}")

# Global troubleshoot manager instance
troubleshoot_manager = TroubleshootManager()
