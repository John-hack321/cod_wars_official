import asyncio
from typing import Optional, List, Dict, Any
from cod_api import API, platforms
from app.core.config import settings

class CodApiService:
    """A service to interact with the unofficial Call of Duty API."""

    def __init__(self, sso_token: Optional[str] = None):
        self.api = API()
        self.sso_token = sso_token or settings.COD_SSO_TOKEN
        self._is_logged_in = False

    async def _ensure_login(self):
        """Ensures the service is logged into the CoD API before making a request."""
        if not self._is_logged_in:
            if not self.sso_token:
                raise ValueError("Call of Duty SSO token is not configured.")
            try:
                await self.api.loginAsync(self.sso_token)
                self._is_logged_in = True
                print("Successfully logged into Call of Duty API.")
            except Exception as e:
                print(f"Error logging into CoD API: {e}")
                raise

    async def search_player(self, platform_str: str, gamertag: str) -> Optional[Dict]:
        """Searches for a player on a given platform."""
        await self._ensure_login()
        try:
            platform = await self._get_platform_enum(platform_str)
            results = await self.api.searchPlayersAsync(platform, gamertag)
            # Find the exact match
            for player in results:
                if player.username.lower() == gamertag.lower():
                    return player.data
            return None
        except Exception as e:
            print(f"Error searching for player {gamertag} on {platform_str}: {e}")
            return None

    async def _get_platform_enum(self, platform_str: str) -> Optional[Any]:
        return getattr(platforms, platform_str.upper())

    async def get_match_history(self, platform_str: str, gamertag: str) -> Optional[List[Dict]]:
        """Gets the Warzone match history for a player."""
        await self._ensure_login()
        try:
            platform = self._get_platform_enum(platform_str)
            history = await self.api.Warzone.combatHistoryAsync(platform, gamertag)
            return history
        except Exception as e:
            print(f"Error getting match history for {gamertag}: {e}")
            return None

    async def get_match_details(self, platform_str: str, match_id: str) -> Optional[Dict]:
        """Gets the full details for a specific Warzone match."""
        await self._ensure_login()
        try:
            platform = await self._get_platform_enum(platform_str)
            match = await self.api.Warzone.matchInfoAsync(match_id, platform)
            return match
        except Exception as e:
            print(f"Error getting details for match {match_id}: {e}")
            return None

    async def verify_match_result(self, match_id: str, platform_str: str, expected_players: List[str]) -> bool:
        """
        Verifies that all expected players were present in the specified match.
        This is a simplified verification. A real implementation would check scores, placement, etc.
        """
        await self._ensure_login()
        try:
            match_details = await self.get_match_details(platform_str, match_id)
            if not match_details or not match_details.get("allPlayers"):
                return False

            present_players = {p.username.lower() for p in match_details["allPlayers"]}
            expected_players_lower = {p.lower() for p in expected_players}

            # Check if all expected players are in the set of present players
            return expected_players_lower.issubset(present_players)
        except Exception as e:
            print(f"Error verifying match {match_id}: {e}")
            return False

# Singleton instance of the service
cod_api_service = CodApiService()

