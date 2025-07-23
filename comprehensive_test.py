#!/usr/bin/env python3
"""
Comprehensive test script for Personal Automation Bot
Tests all 7 main functionalities both locally and through Telegram
"""

import asyncio
import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import bot components
from personal_automation_bot.bot.core import PersonalAutomationBot
from personal_automation_bot.config import settings
from personal_automation_bot.services.email.email_service import EmailService
from personal_automation_bot.services.calendar.calendar_service import CalendarService
from personal_automation_bot.services.content.text_generator import get_text_generator
from personal_automation_bot.services.documents.document_service import DocumentService
from personal_automation_bot.services.flows.engine import FlowEngine
from simple_rag_service import SimpleRAGService
from simple_flow_engine import SimpleFlowEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveTest:
    def __init__(self):
        self.settings = settings
        self.test_results = {}
        self.telegram_chat_id = None  # Will be set when we get a message

    async def setup_environment(self):
        """Setup the test environment"""
        logger.info("🔧 Setting up test environment...")

        # Activate virtual environment if it exists
        venv_path = Path("venv")
        if venv_path.exists():
            logger.info("Virtual environment found, activating...")
            # The environment should already be activated by the calling script

        # Verify all required environment variables
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
            logger.error(f"❌ Missing environment variables: {missing_vars}")
            return False

        logger.info("✅ Environment setup complete")
        return True

    async def test_1_telegram_bot_control(self):
        """Test 1: Telegram Bot Control - Basic commands and interface"""
        logger.info("🤖 Testing Telegram Bot Control...")

        try:
            # Initialize bot
            bot = PersonalAutomationBot()

            # Test bot initialization
            if bot.application:
                self.test_results['telegram_bot'] = {
                    'status': 'PASS',
                    'details': 'Bot initialized successfully',
                    'timestamp': datetime.now().isoformat()
                }
                logger.info("✅ Telegram bot initialized successfully")

                # Start bot in background for integration tests
                logger.info("🚀 Starting Telegram bot for integration testing...")
                await bot.start_bot_async()

                return True
            else:
                raise Exception("Bot initialization failed")

        except Exception as e:
            self.test_results['telegram_bot'] = {
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"❌ Telegram bot test failed: {e}")
            return False

    async def test_2_email_management(self):
        """Test 2: Email Management - Gmail integration"""
        logger.info("📧 Testing Email Management...")

        try:
            email_service = EmailService()

            # Test email service initialization
            if hasattr(email_service, 'gmail_client'):
                # Test reading emails (this will require authentication)
                logger.info("Testing email reading capability...")

                # For now, just test that the service can be initialized
                self.test_results['email_management'] = {
                    'status': 'PASS',
                    'details': 'Email service initialized, authentication required for full functionality',
                    'timestamp': datetime.now().isoformat()
                }
                logger.info("✅ Email service initialized successfully")
                return True
            else:
                raise Exception("Email service initialization failed")

        except Exception as e:
            self.test_results['email_management'] = {
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"❌ Email management test failed: {e}")
            return False

    async def test_3_calendar_management(self):
        """Test 3: Calendar Management - Google Calendar integration"""
        logger.info("📅 Testing Calendar Management...")

        try:
            calendar_service = CalendarService()

            # Test calendar service initialization
            if hasattr(calendar_service, 'calendar_client'):
                self.test_results['calendar_management'] = {
                    'status': 'PASS',
                    'details': 'Calendar service initialized, authentication required for full functionality',
                    'timestamp': datetime.now().isoformat()
                }
                logger.info("✅ Calendar service initialized successfully")
                return True
            else:
                raise Exception("Calendar service initialization failed")

        except Exception as e:
            self.test_results['calendar_management'] = {
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"❌ Calendar management test failed: {e}")
            return False

    async def test_4_content_generation(self):
        """Test 4: Content Generation - AI with Groq"""
        logger.info("🎨 Testing Content Generation...")

        try:
            text_generator = get_text_generator(provider="groq")

            # Test text generation
            test_prompt = "Generate a short motivational message about productivity"
            logger.info(f"Testing text generation with prompt: {test_prompt}")

            generated_text = text_generator.generate(test_prompt, max_tokens=100)

            if generated_text and len(generated_text.strip()) > 0:
                self.test_results['content_generation'] = {
                    'status': 'PASS',
                    'details': f'Successfully generated text: {generated_text[:100]}...',
                    'timestamp': datetime.now().isoformat()
                }
                logger.info("✅ Content generation test passed")
                return True
            else:
                raise Exception("Generated text is empty")

        except Exception as e:
            self.test_results['content_generation'] = {
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"❌ Content generation test failed: {e}")
            return False

    async def test_5_document_storage(self):
        """Test 5: Document Storage - Google Drive/Notion integration"""
        logger.info("📄 Testing Document Storage...")

        try:
            document_service = DocumentService()

            # Test document service initialization
            if hasattr(document_service, 'storage_manager'):
                # Test saving a simple document locally
                test_content = "This is a test document for the automation bot"
                test_title = f"Test Document {datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # Save document locally first (using a simple approach)
                from personal_automation_bot.services.documents.models import StorageBackend
                doc_metadata = document_service.create_document(
                    user_id=12345,  # Test user ID
                    title=test_title,
                    content=test_content,
                    backend=StorageBackend.GOOGLE_DRIVE,
                    tags=['test', 'automation']
                )
                doc_id = doc_metadata.id if doc_metadata else None

                if doc_id:
                    self.test_results['document_storage'] = {
                        'status': 'PASS',
                        'details': f'Document saved successfully with ID: {doc_id}',
                        'timestamp': datetime.now().isoformat()
                    }
                    logger.info("✅ Document storage test passed")
                    return True
                else:
                    raise Exception("Document save returned no ID")
            else:
                raise Exception("Document service initialization failed")

        except Exception as e:
            self.test_results['document_storage'] = {
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"❌ Document storage test failed: {e}")
            return False

    async def test_6_rag_system(self):
        """Test 6: RAG System - Document-based content generation"""
        logger.info("🧠 Testing RAG System...")

        try:
            rag_service = SimpleRAGService()

            # Test RAG service initialization
            if hasattr(rag_service, 'vector_store'):
                # Create a test document for indexing
                test_doc_content = """
                Personal Automation Bot is a comprehensive system for managing productivity tasks.
                It integrates with Gmail for email management, Google Calendar for scheduling,
                and uses AI for content generation. The system is designed to work with free
                services and can be deployed locally or on free hosting platforms.
                """

                # Index the test document
                logger.info("Indexing test document...")
                doc_id = await rag_service.index_document(
                    content=test_doc_content,
                    title="Personal Automation Bot Overview",
                    metadata={'type': 'documentation', 'category': 'system'}
                )

                if doc_id:
                    # Test RAG generation
                    logger.info("Testing RAG-based content generation...")
                    query = "What services does the Personal Automation Bot integrate with?"

                    response = await rag_service.generate_with_context(query)

                    if response and len(response.strip()) > 0:
                        self.test_results['rag_system'] = {
                            'status': 'PASS',
                            'details': f'RAG generation successful: {response[:100]}...',
                            'timestamp': datetime.now().isoformat()
                        }
                        logger.info("✅ RAG system test passed")
                        return True
                    else:
                        raise Exception("RAG generation returned empty response")
                else:
                    raise Exception("Document indexing failed")
            else:
                raise Exception("RAG service initialization failed")

        except Exception as e:
            self.test_results['rag_system'] = {
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"❌ RAG system test failed: {e}")
            return False

    async def test_7_workflow_automation(self):
        """Test 7: Workflow Automation - Flows and triggers"""
        logger.info("⚙️ Testing Workflow Automation...")

        try:
            flow_engine = SimpleFlowEngine()

            # Test flow engine initialization
            if hasattr(flow_engine, 'flows'):
                # Create a simple test flow
                test_flow = {
                    'name': 'Test Automation Flow',
                    'trigger': {
                        'type': 'command',
                        'parameters': {'command': 'test_flow'}
                    },
                    'actions': [
                        {
                            'service': 'content',
                            'method': 'generate_text',
                            'parameters': {'prompt': 'Generate a test message'}
                        }
                    ]
                }

                # Create the flow
                flow_id = await flow_engine.create_flow(test_flow)

                if flow_id:
                    # Test flow execution
                    logger.info("Testing flow execution...")
                    result = await flow_engine.execute_flow(flow_id)

                    if result:
                        self.test_results['workflow_automation'] = {
                            'status': 'PASS',
                            'details': f'Flow created and executed successfully: {flow_id}',
                            'timestamp': datetime.now().isoformat()
                        }
                        logger.info("✅ Workflow automation test passed")
                        return True
                    else:
                        raise Exception("Flow execution failed")
                else:
                    raise Exception("Flow creation failed")
            else:
                raise Exception("Flow engine initialization failed")

        except Exception as e:
            self.test_results['workflow_automation'] = {
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"❌ Workflow automation test failed: {e}")
            return False

    async def send_telegram_notification(self, message):
        """Send notification to Telegram about test results"""
        try:
            if self.telegram_chat_id:
                from telegram import Bot
                bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
                await bot.send_message(chat_id=self.telegram_chat_id, text=message)
                logger.info(f"📱 Sent Telegram notification: {message[:50]}...")
            else:
                logger.warning("No Telegram chat ID available for notifications")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

    async def run_all_tests(self):
        """Run all tests in sequence"""
        logger.info("🚀 Starting comprehensive test suite...")

        # Setup environment
        if not await self.setup_environment():
            logger.error("❌ Environment setup failed, aborting tests")
            return

        # List of test functions
        tests = [
            ('Telegram Bot Control', self.test_1_telegram_bot_control),
            ('Email Management', self.test_2_email_management),
            ('Calendar Management', self.test_3_calendar_management),
            ('Content Generation', self.test_4_content_generation),
            ('Document Storage', self.test_5_document_storage),
            ('RAG System', self.test_6_rag_system),
            ('Workflow Automation', self.test_7_workflow_automation),
        ]

        # Run each test
        passed_tests = 0
        total_tests = len(tests)

        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'='*50}")

            try:
                success = await test_func()
                if success:
                    passed_tests += 1
                    await self.send_telegram_notification(f"✅ {test_name} - PASSED")
                else:
                    await self.send_telegram_notification(f"❌ {test_name} - FAILED")
            except Exception as e:
                logger.error(f"Test {test_name} crashed: {e}")
                await self.send_telegram_notification(f"💥 {test_name} - CRASHED: {str(e)}")

        # Generate final report
        await self.generate_final_report(passed_tests, total_tests)

    async def generate_final_report(self, passed_tests, total_tests):
        """Generate and send final test report"""
        logger.info(f"\n{'='*60}")
        logger.info("FINAL TEST REPORT")
        logger.info(f"{'='*60}")

        report = f"""
🤖 Personal Automation Bot - Test Results

📊 Summary:
✅ Passed: {passed_tests}/{total_tests}
❌ Failed: {total_tests - passed_tests}/{total_tests}
📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%

📋 Detailed Results:
"""

        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result['status'] == 'PASS' else "❌"
            report += f"{status_emoji} {test_name.replace('_', ' ').title()}: {result['status']}\n"
            if result['status'] == 'PASS':
                report += f"   Details: {result.get('details', 'No details')}\n"
            else:
                report += f"   Error: {result.get('error', 'Unknown error')}\n"
            report += "\n"

        report += f"🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        logger.info(report)

        # Send final report to Telegram
        await self.send_telegram_notification(report)

        # Save report to file
        with open('test_report.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)

        logger.info("📄 Test report saved to test_report.json")

async def main():
    """Main function to run all tests"""
    tester = ComprehensiveTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
