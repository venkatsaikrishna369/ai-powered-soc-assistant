import openai
from typing import List, Dict, Any
import json
import asyncio
import re
from datetime import datetime

from config.settings import OPENAI_API_KEY, MITRE_TECHNIQUES

class FastLLMService:
    def __init__(self):
        # YOUR API KEY IS USED HERE
        self.api_key = OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=self.api_key)
        self.cache = {}
        self.request_delay = 0.2
        
        # Test connection
        print(f"✓ OpenAI API Key: {'Configured' if self.api_key else 'Not configured'}")
    
    async def analyze_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """Analyze alerts with MITRE mapping"""
        enhanced_alerts = []
        
        for alert in alerts:
            # Only use LLM for critical/high alerts for speed
            if alert.get('severity') in ['critical', 'high']:
                enhanced = await self._analyze_with_openai(alert)
            else:
                enhanced = self._fast_mapping(alert)
            
            enhanced_alerts.append(enhanced)
        
        return enhanced_alerts
    
    async def _analyze_with_openai(self, alert: Dict) -> Dict:
        """Analyze alert using OpenAI"""
        alert_id = alert.get('id', '')
        
        # Check cache
        if alert_id in self.cache:
            return self.cache[alert_id]
        
        try:
            # Rate limiting
            await asyncio.sleep(self.request_delay)
            
            # Prepare prompt
            prompt = self._create_prompt(alert)
            
            # Call OpenAI
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity SOC analyst. Return JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse response
            content = response.choices[0].message.content
            analysis = self._parse_response(content)
            
            # Merge with alert
            enhanced = {
                **alert,
                'llm_analysis': analysis.get('analysis', ''),
                'mitre_techniques': analysis.get('mitre_techniques', ['T1046']),
                'mitre_tactics': analysis.get('mitre_tactics', ['Discovery']),
                'recommended_actions': analysis.get('recommended_actions', ['Review logs']),
                'risk_level': analysis.get('risk_level', 'medium')
            }
            
            # Cache
            self.cache[alert_id] = enhanced
            
            return enhanced
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._fast_mapping(alert)
    
    def _create_prompt(self, alert: Dict) -> str:
        """Create prompt for OpenAI"""
        return f"""Analyze this security alert and provide MITRE ATT&CK mapping:

Alert Details:
- Severity: {alert.get('severity', 'unknown')}
- Source: {alert.get('source_ip', 'unknown')}
- Destination: {alert.get('destination_ip', 'unknown')}
- Description: {alert.get('description', 'unknown')}
- Confidence: {alert.get('confidence', 0)}

Return JSON with this structure:
{{
    "analysis": "brief analysis",
    "mitre_techniques": ["T1046", "T1190"],
    "mitre_tactics": ["Discovery", "Initial Access"],
    "recommended_actions": ["action1", "action2"],
    "risk_level": "critical/high/medium/low"
}}"""
    
    def _parse_response(self, content: str) -> Dict:
        """Parse OpenAI response"""
        try:
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Default response
        return {
            "analysis": content[:150] if content else "AI analysis completed",
            "mitre_techniques": ["T1046"],
            "mitre_tactics": ["Discovery"],
            "recommended_actions": ["Block source IP", "Review firewall logs"],
            "risk_level": "medium"
        }
    
    def _fast_mapping(self, alert: Dict) -> Dict:
        """Fast MITRE mapping without LLM"""
        severity = alert.get('severity', 'medium')
        
        # Map severity to techniques
        technique_map = {
            'critical': ['T1190', 'T1133', 'T1566'],
            'high': ['T1046', 'T1043', 'T1059'],
            'medium': ['T1203', 'T1064'],
            'low': ['T1547', 'T1136'],
            'info': ['T1083']
        }
        
        tactics_map = {
            'critical': ['Initial Access', 'Execution'],
            'high': ['Discovery', 'Command & Control'],
            'medium': ['Persistence', 'Privilege Escalation'],
            'low': ['Defense Evasion'],
            'info': ['Discovery']
        }
        
        techniques = technique_map.get(severity, ['T1046'])
        tactics = tactics_map.get(severity, ['Discovery'])
        
        return {
            **alert,
            'llm_analysis': f"{severity.upper()} severity alert requiring attention.",
            'mitre_techniques': techniques,
            'mitre_tactics': tactics,
            'recommended_actions': [
                'Monitor network traffic',
                'Review system logs',
                'Update firewall rules'
            ],
            'risk_level': severity
        }
    
    async def generate_threat_intel(self) -> Dict:
        """Generate threat intelligence"""
        try:
            prompt = """Provide current threat intelligence analysis including:
            1. Root cause of recent threats
            2. Top MITRE techniques observed
            3. Recommended security actions
            
            Return as JSON with keys: root_cause, top_threats, recommendations"""
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a threat intelligence analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            return self._parse_intel(content)
            
        except Exception as e:
            print(f"Threat intel error: {e}")
            return self._default_intel()
    
    def _parse_intel(self, content: str) -> Dict:
        """Parse threat intelligence"""
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return self._default_intel()
    
    def _default_intel(self) -> Dict:
        """Default threat intelligence"""
        return {
            "root_cause": "Increased scanning activity from suspicious IP ranges. Possible reconnaissance phase of attack.",
            "top_threats": ["Port Scanning (T1046)", "Network Discovery (T1043)", "Credential Stuffing"],
            "recommendations": [
                "Implement rate limiting on authentication endpoints",
                "Block known malicious IP ranges",
                "Enable multi-factor authentication"
            ]
        }

# Global instance
llm_service = FastLLMService()