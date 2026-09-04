"""
P Plugin v3.8.1 - Agent Health Check & Diagnostics
Run this to check why agents are showing as "暂时不可用"
"""
import asyncio
import httpx

API_BASE = "http://127.0.0.1:8088"

async def check_agents_health():
    """Check agent health"""
    print("=" * 60)
    print("🔍 P Plugin Agent Health Check")
    print("=" * 60)
    
    # 1. Check if P Plugin API is accessible
    print("\n1. Checking P Plugin API...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{API_BASE}/api/plugins/p_plugin/agents")
            if resp.status_code == 200:
                data = resp.json()
                print(f"   ✅ P Plugin API OK")
                print(f"   📊 Found {data.get('count', 0)} agents")
                print(f"   🔗 API Accessible: {data.get('health', {}).get('api_accessible', False)}")
                
                # List agents
                print("\n   🤖 Available Agents:")
                for agent in data.get("agents", []):
                    print(f"      - {agent.get('icon')} {agent.get('name')} ({agent.get('id')})")
            else:
                print(f"   ❌ P Plugin API returned {resp.status_code}")
    except Exception as e:
        print(f"   ❌ P Plugin API Error: {e}")
    
    # 2. Check QwenPaw Agents API
    print("\n2. Checking QwenPaw Agents API...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{API_BASE}/api/agents")
            print(f"   Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                agents = data.get("agents", [])
                print(f"   ✅ Found {len(agents)} agents in QwenPaw")
                for a in agents[:5]:
                    print(f"      - {a.get('name')} ({a.get('id')})")
            else:
                print(f"   ❌ Response: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Test agent chat endpoint
    print("\n3. Testing Agent Chat Endpoint...")
    test_agents = ["default", "QwenPaw_QA_Agent_0.2", "cloud-orchestrator"]
    for agent_id in test_agents:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{API_BASE}/api/agents/{agent_id}/chat",
                    json={"message": "hello", "session_id": f"test:{agent_id}"},
                    timeout=10.0
                )
                status = "✅" if resp.status_code == 200 else "❌"
                print(f"   {status} {agent_id}: {resp.status_code}")
        except Exception as e:
            print(f"   ❌ {agent_id}: {e}")
    
    # 4. Check Console Chat API
    print("\n4. Checking Console Chat API...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{API_BASE}/api/console/chat",
                json={"message": "hello", "agent_id": "default"},
                timeout=10.0
            )
            print(f"   Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"   ✅ Console Chat API OK")
            else:
                print(f"   ❌ Response: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("💡 Recommendations:")
    print("=" * 60)
    print("""
If agents show "暂时不可用":

1. Check if QwenPaw is running:
   curl http://127.0.0.1:8088/api/agents

2. Check agent.json configuration:
   - Agents must be enabled
   - Channels must be configured

3. Restart QwenPaw after plugin updates:
   qwenpaw restart

4. Check logs:
   ~/.qwenpaw/logs/p_plugin.log

5. The fallback response system will provide basic responses
   even if agent APIs are unavailable.
""")

if __name__ == "__main__":
    asyncio.run(check_agents_health())
