#!/usr/bin/env python3
"""
Final verification test for all Personal Automation Bot functionalities
"""
import asyncio
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalVerificationTest:
    def __init__(self):
        self.results = {}

    async def test_1_telegram_bot_setup(self):
        """Test 1: Verify Telegram bot setup and configuration"""
        logger.info("🤖 Testing Telegram Bot Setup...")

        try:
            from telegram import Bot
            from personal_automation_bot.bot.core import setup_bot

            # Test bot token
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                raise Exception("TELEGRAM_BOT_TOKEN not found")

            # Test bot creation
            bot = Bot(token=bot_token)
            bot_info = await bot.get_me()

            # Test bot setup
            app = setup_bot(bot_token)

            self.results['telegram_bot'] = {
                'status': 'PASS',
                'bot_username': bot_info.username,
                'bot_id': bot_info.id,
                'handlers_count': len(app.handlers[0])
            }

            logger.info(f"✅ Telegram Bot Setup - Bot: @{bot_info.username}")
            return True

        except Exception as e:
            self.results['telegram_bot'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Telegram Bot Setup failed: {e}")
            return False

    async def test_2_email_service(self):
        """Test 2: Email service initialization"""
        logger.info("📧 Testing Email Service...")

        try:
            from personal_automation_bot.services.email.email_service import EmailService

            email_service = EmailService()

            # Test service initialization
            if hasattr(email_service, '_clients'):
                self.results['email_service'] = {
                    'status': 'PASS',
                    'note': 'Service initialized, requires user authentication for full functionality'
                }
                logger.info("✅ Email Service - Initialized successfully")
                return True
            else:
                raise Exception("Email service missing required attributes")

        except Exception as e:
            self.results['email_service'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Email Service failed: {e}")
            return False

    async def test_3_calendar_service(self):
        """Test 3: Calendar service initialization"""
        logger.info("📅 Testing Calendar Service...")

        try:
            from personal_automation_bot.services.calendar.calendar_service import CalendarService

            calendar_service = CalendarService()

            # Test service initialization
            if hasattr(calendar_service, 'auth_manager'):
                self.results['calendar_service'] = {
                    'status': 'PASS',
                    'note': 'Service initialized, requires user authentication for full functionality'
                }
                logger.info("✅ Calendar Service - Initialized successfully")
                return True
            else:
                raise Exception("Calendar service missing required attributes")

        except Exception as e:
            self.results['calendar_service'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Calendar Service failed: {e}")
            return False

    async def test_4_content_generation(self):
        """Test 4: AI Content generation with Groq"""
        logger.info("🎨 Testing Content Generation...")

        try:
            from personal_automation_bot.services.content.text_generator import get_text_generator

            # Test Groq text generation
            generator = get_text_generator(provider="groq")

            test_prompt = "Write a brief welcome message for a productivity automation bot"
            result = generator.generate(test_prompt, max_tokens=100)

            if result and len(result.strip()) > 10:
                self.results['content_generation'] = {
                    'status': 'PASS',
                    'provider': 'Groq',
                    'sample_output': result[:100] + "..." if len(result) > 100 else result
                }
                logger.info("✅ Content Generation - Working with Groq")
                return True
            else:
                raise Exception("Generated content is empty or too short")

        except Exception as e:
            self.results['content_generation'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Content Generation failed: {e}")
            return False

    async def test_5_document_storage(self):
        """Test 5: Document storage service"""
        logger.info("📄 Testing Document Storage...")

        try:
            from personal_automation_bot.services.documents.document_service import DocumentService

            doc_service = DocumentService()

            # Test service initialization
            if hasattr(doc_service, 'storage_manager'):
                self.results['document_storage'] = {
                    'status': 'PASS',
                    'note': 'Service initialized, supports Google Drive and Notion backends'
                }
                logger.info("✅ Document Storage - Service initialized")
                return True
            else:
                raise Exception("Document service missing required attributes")

        except Exception as e:
            self.results['document_storage'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Document Storage failed: {e}")
            return False

    async def test_6_rag_system(self):
        """Test 6: RAG (Retrieval-Augmented Generation) system"""
        logger.info("🧠 Testing RAG System...")

        try:
            # Use our simple RAG service for testing
            from simple_rag_service import SimpleRAGService

            rag_service = SimpleRAGService()

            # Test document indexing
            test_content = """
            Personal Automation Bot is a comprehensive productivity system.
            It integrates with Gmail, Google Calendar, and AI services.
            The bot helps automate daily tasks and content creation.
            """

            doc_id = await rag_service.index_document(
                content=test_content,
                title="Test Document",
                metadata={'category': 'test'}
            )

            # Test RAG generation
            query = "What does the Personal Automation Bot integrate with?"
            response = await rag_service.generate_with_context(query)

            if doc_id and response and len(response.strip()) > 10:
                self.results['rag_system'] = {
                    'status': 'PASS',
                    'indexed_docs': 1,
                    'sample_response': response[:100] + "..." if len(response) > 100 else response
                }
                logger.info("✅ RAG System - Document indexing and generation working")
                return True
            else:
                raise Exception("RAG system failed to index or generate content")

        except Exception as e:
            self.results['rag_system'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ RAG System failed: {e}")
            return False

    async def test_7_workflow_automation(self):
        """Test 7: Workflow automation system"""
        logger.info("⚙️ Testing Workflow Automation...")

        try:
            from simple_flow_engine import SimpleFlowEngine

            flow_engine = SimpleFlowEngine()

            # Test flow creation
            test_flow = {
                'name': 'Test Productivity Flow',
                'trigger': {'type': 'command', 'command': 'test'},
                'actions': [
                    {'service': 'content', 'method': 'generate', 'params': {'prompt': 'test'}}
                ]
            }

            flow_id = await flow_engine.create_flow(test_flow)

            # Test flow execution
            result = await flow_engine.execute_flow(flow_id)

            if flow_id and result and result.get('success'):
                self.results['workflow_automation'] = {
                    'status': 'PASS',
                    'flow_id': flow_id,
                    'execution_result': 'Success'
                }
                logger.info("✅ Workflow Automation - Flow creation and execution working")
                return True
            else:
                raise Exception("Flow creation or execution failed")

        except Exception as e:
            self.results['workflow_automation'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Workflow Automation failed: {e}")
            return False

    async def test_environment_setup(self):
        """Test environment and configuration"""
        logger.info("🔧 Testing Environment Setup...")

        try:
            required_vars = [
                'TELEGRAM_BOT_TOKEN',
                'GOOGLE_CLIENT_ID',
                'GOOGLE_CLIENT_SECRET',
                'GROQ_API_KEY'
            ]

            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)

            if missing_vars:
                raise Exception(f"Missing environment variables: {missing_vars}")

            self.results['environment'] = {
                'status': 'PASS',
                'required_vars': len(required_vars),
                'configured_vars': len(required_vars) - len(missing_vars)
            }

            logger.info("✅ Environment Setup - All required variables configured")
            return True

        except Exception as e:
            self.results['environment'] = {'status': 'FAIL', 'error': str(e)}
            logger.error(f"❌ Environment Setup failed: {e}")
            return False

    async def run_all_tests(self):
        """Run all verification tests"""
        logger.info("🚀 Starting Final Verification Test Suite...")
        logger.info("="*60)

        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("Telegram Bot Setup", self.test_1_telegram_bot_setup),
            ("Email Service", self.test_2_email_service),
            ("Calendar Service", self.test_3_calendar_service),
            ("Content Generation", self.test_4_content_generation),
            ("Document Storage", self.test_5_document_storage),
            ("RAG System", self.test_6_rag_system),
            ("Workflow Automation", self.test_7_workflow_automation),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            logger.info(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if await test_func():
                    passed += 1
            except Exception as e:
                logger.error(f"Test {test_name} crashed: {e}")

        # Generate final report
        await self.generate_final_report(passed, total)

    async def generate_final_report(self, passed, total):
        """Generate final verification report"""
        logger.info("\n" + "="*60)
        logger.info("🎯 FINAL VERIFICATION REPORT")
        logger.info("="*60)

        success_rate = (passed / total) * 100

        print(f"""
🤖 Personal Automation Bot - Final Verification Results

📊 OVERALL RESULTS:
✅ Passed: {passed}/{total} tests
📈 Success Rate: {success_rate:.1f}%

📋 DETAILED RESULTS:
""")

        for test_name, result in self.results.items():
            status_emoji = "✅" if result['status'] == 'PASS' else "❌"
            test_display = test_name.replace('_', ' ').title()

            print(f"{status_emoji} {test_display}: {result['status']}")

            if result['status'] == 'PASS':
                if 'note' in result:
                    print(f"   📝 {result['note']}")
                if 'sample_output' in result:
                    print(f"   💬 Sample: {result['sample_output']}")
                if 'bot_username' in result:
                    print(f"   🤖 Bot: @{result['bot_username']}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            print()

        print("🎯 SUMMARY:")
        if success_rate >= 80:
            print("🎉 EXCELLENT! Bot is ready for production use")
        elif success_rate >= 60:
            print("✅ GOOD! Most features working, minor issues to resolve")
        else:
            print("⚠️ NEEDS WORK! Several critical issues to address")

        print(f"""
🚀 NEXT STEPS:
1. Start the bot: python main.py
2. Send /start to @{self.results.get('telegram_bot', {}).get('bot_username', 'your_bot')}
3. Use /auth to authenticate with Google services
4. Test email and calendar features
5. Create custom workflows and content

📅 Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

async def main():
    """Main test function"""
    tester = FinalVerificationTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
