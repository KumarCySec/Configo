#!/usr/bin/env python3
"""
Final Test Summary for CONFIGO Environment Intelligence
======================================================

This script runs a comprehensive test suite to verify all improvements
made to the CONFIGO environment intelligence system.
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.enhanced_llm_agent import EnhancedLLMAgent
from core.memory import AgentMemory
from core.ai import LLMClient

def test_enhanced_llm_agent():
    """Test the enhanced LLM agent functionality."""
    print("🧪 Testing Enhanced LLM Agent")
    print("=" * 50)
    
    try:
        # Initialize components
        memory = AgentMemory()
        agent = EnhancedLLMAgent(memory)
        
        # Test different domains
        test_cases = [
            "AI Developer",
            "Web Developer (React)",
            "Data Scientist", 
            "DevOps Engineer"
        ]
        
        results = []
        for test_case in test_cases:
            print(f"\n🔍 Testing: {test_case}")
            result = agent.generate_enhanced_stack(test_case, "")
            
            tools_count = len(result.tools)
            portals_count = len(result.login_portals)
            domain = result.domain_completion.get("detected_domain", "unknown")
            
            print(f"  📦 Tools: {tools_count}")
            print(f"  🌐 Portals: {portals_count}")
            print(f"  🎯 Domain: {domain}")
            print(f"  ✅ Target Met (8+ tools): {tools_count >= 8}")
            
            results.append({
                'case': test_case,
                'tools': tools_count,
                'portals': portals_count,
                'domain': domain,
                'target_met': tools_count >= 8
            })
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"  • Total test cases: {len(results)}")
        print(f"  • Cases meeting target: {sum(1 for r in results if r['target_met'])}")
        print(f"  • Average tools per case: {sum(r['tools'] for r in results) / len(results):.1f}")
        print(f"  • Average portals per case: {sum(r['portals'] for r in results) / len(results):.1f}")
        
        return all(r['target_met'] for r in results)
        
    except Exception as e:
        print(f"❌ Enhanced LLM Agent test failed: {e}")
        return False

def test_memory_integration():
    """Test memory system integration."""
    print("\n🧠 Testing Memory Integration")
    print("=" * 50)
    
    try:
        memory = AgentMemory()
        
        # Test basic memory operations
        session_id = memory.start_session("test_session")
        memory.record_tool_installation("test_tool", "test_cmd", "test_check", True, "1.0.0")
        memory.end_session(session_id)
        
        print("✅ Memory operations successful")
        return True
        
    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")
        return False

def test_domain_detection():
    """Test domain detection accuracy."""
    print("\n🎯 Testing Domain Detection")
    print("=" * 50)
    
    try:
        memory = AgentMemory()
        agent = EnhancedLLMAgent(memory)
        
        test_cases = [
            ("AI Developer", "ai_ml"),
            ("Web Developer", "web_dev"),
            ("Data Scientist", "data_science"),
            ("DevOps Engineer", "devops")
        ]
        
        correct_detections = 0
        for input_text, expected_domain in test_cases:
            result = agent.generate_enhanced_stack(input_text, "")
            detected_domain = result.domain_completion.get("detected_domain", "unknown")
            
            is_correct = detected_domain == expected_domain
            status = "✅" if is_correct else "❌"
            print(f"  {status} {input_text} -> {detected_domain} (expected: {expected_domain})")
            
            if is_correct:
                correct_detections += 1
        
        accuracy = correct_detections / len(test_cases)
        print(f"\n📊 Domain Detection Accuracy: {accuracy:.1%} ({correct_detections}/{len(test_cases)})")
        
        return accuracy >= 0.75  # 75% accuracy threshold
        
    except Exception as e:
        print(f"❌ Domain detection test failed: {e}")
        return False

def test_fallback_system():
    """Test fallback system when LLM fails."""
    print("\n🔄 Testing Fallback System")
    print("=" * 50)
    
    try:
        memory = AgentMemory()
        agent = EnhancedLLMAgent(memory)
        
        # Test with a domain that should trigger fallback
        result = agent.generate_enhanced_stack("Test Domain", "")
        
        tools_count = len(result.tools)
        fallback_used = result.domain_completion.get("fallback", False)
        
        print(f"  📦 Tools generated: {tools_count}")
        print(f"  🔄 Fallback used: {fallback_used}")
        print(f"  ✅ Minimum tools met: {tools_count >= 3}")
        
        return tools_count >= 3  # Should have at least 3 tools even with fallback
        
    except Exception as e:
        print(f"❌ Fallback system test failed: {e}")
        return False

def main():
    """Run the complete test suite."""
    print("🚀 CONFIGO Environment Intelligence - Final Test Suite")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    tests = [
        ("Enhanced LLM Agent", test_enhanced_llm_agent),
        ("Memory Integration", test_memory_integration),
        ("Domain Detection", test_domain_detection),
        ("Fallback System", test_fallback_system)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 FINAL TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! CONFIGO Environment Intelligence is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 