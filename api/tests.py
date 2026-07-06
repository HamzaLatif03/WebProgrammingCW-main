"""
Command to run tests:

python manage.py test 

or 

python manage.py test api.tests.AuthenticationTests

"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .models import CustomUser,Hobby
from selenium.webdriver.common.keys import Keys

class AuthenticationTests(StaticLiveServerTestCase):
    @classmethod
    def init_driver(cls):
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        print("\n🚀 Initializing Chrome WebDriver...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.wait = WebDriverWait(driver, 5)
        driver.maximize_window()
        print("✅ WebDriver initialized successfully")
        return driver
    
    test_results={}

    @classmethod
    def setUpClass(cls):
        print("\n🔧 Setting up test environment...")
        cls.host = "localhost"
        # cls.selennium = WebDriver()
        # cls.port = 8000
        # cls.frontend_port = 5173
        super().setUpClass()
        cls.driver = cls.init_driver()
        print("✅ Test environment setup complete")
    
    
    @classmethod
    def tearDownClass(cls):
        print("\n📊 Test Summary")
        print("---------------")
        
        # Print stored test results
        for test_num in range(1, 7):
            test_key = f'test_{test_num}'
            result = cls.test_results.get(test_key, "No result recorded")
            status = "✅" if "Failed" not in result else "❌"
            print(f"{status} Test {test_num}: {result}")

        print("\n🧹 Cleaning up test environment...")
        import logging
        logging.getLogger('django.server').setLevel(logging.ERROR)
        if hasattr(cls, 'driver'):
            try:
                cls.driver.quit()
            except:
                pass
            print("✅ WebDriver closed successfully")
        super().tearDownClass()

    def setUp(self):
        
        print("\n📝 Creating test users...")
        existing_user = CustomUser.objects.filter(username='testuser').first()
        self.reading_hobby = Hobby.objects.create(hobby_name='Reading')
        if existing_user:
            existing_user.delete()
        
        self.test_user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            name='Test User',
            date_of_birth='1990-01-01'
        )
        
        # Create second test user for friend requests
        existing_user2 = CustomUser.objects.filter(username='testuser2').first()
        if existing_user2:
            existing_user2.delete()
            
        self.test_user2 = CustomUser.objects.create_user(
            username='testuser2',
            password='testpass123',
            email='test2@example.com',
            name='Test User 2',
            date_of_birth='1995-01-01',
        )
        self.test_user2.hobbies.add(self.reading_hobby)
        
        # Create numbered users for filtering/pagination tests
        for i in range(1, 13):
            birth_year = 2024 - (i * 5)
            username = f"username{i}"
            
            existing_user = CustomUser.objects.filter(username=username).first()
            if existing_user:
                existing_user.delete()
                
            CustomUser.objects.create_user(
                username=username,
                password=f"password{i}",
                email=f"email{i}@example.com", 
                name=f"Name {i}",
                date_of_birth=f"{birth_year}-01-01"
            )
        
            
        final_count = CustomUser.objects.count()
        print(f"Database state after setUp: {final_count} users")
        

        print(f"✅ Created {CustomUser.objects.count()} test users")

    def test_1_successful_signup(self):
        print("\n🧪 TEST CASE 1: User Signup")
        print("-------------------------")
        try:
            print("Step 1: Navigating to signup page...")
            
            self.driver.get(f'{self.live_server_url}/api/signup/')

            users_before = CustomUser.objects.count()
            print(f"Total users before signup: {users_before}")
            
            print("\nStep 2: Filling signup form...")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys("newuser")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "id_email"))).send_keys("newuser@example.com")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "id_name"))).send_keys("New User")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "id_date_of_birth"))).send_keys("01-01-1990")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "id_password"))).send_keys("newpass123")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "id_confirm_password"))).send_keys("newpass123")
            time.sleep(1)
            print("\nStep 3: Submitting form...")
            submit_button = self.driver.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)
            submit_button.click()
            
            users_after = CustomUser.objects.count()
            print(f"Total users after signup: {users_after}")
            
            time.sleep(1)
            print("\nStep 4: Verifying results...")
            assert "/api/login/" in self.driver.current_url, "❌ Redirect to login page failed"
            assert CustomUser.objects.filter(username="newuser").exists(), "❌ User was not created"
            assert users_after == users_before + 1, "❌ User not created"
            print("✅ TEST PASSED: Signup successful")
            
            self.__class__.test_results['test_1'] = f"Signup successful - Users before: {users_before}, Users after: {users_after}"
                
            
            
        except Exception as e:
            self.driver.save_screenshot('signup_error.png')
            print(f"❌ TEST FAILED: {str(e)}")
            self.__class__.test_results['test_1'] = f"Failed - {str(e)}"
            raise

    def test_2_successful_login(self):
        print("\n🧪 TEST CASE 2: User Login")
        print("------------------------")
        try:
            print("Step 1: Navigating to login page...")
            self.driver.get(f'{self.live_server_url}/api/login/')
            
            print("\nStep 2: Entering credentials...")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("testuser")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys("testpass123")
            time.sleep(1)
            
            print("\nStep 3: Submitting login form...")
            self.driver.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
            
            time.sleep(1)
            print("\nStep 4: Verifying redirect...")
            expected_url = f"{self.live_server_url}/"
            assert self.driver.current_url == expected_url, f"❌ Wrong redirect URL: {self.driver.current_url}"
            print("✅ TEST PASSED: Login successful")
            self.__class__.test_results['test_2'] = "Login successful - User redirected to homepage"
            
        except Exception as e:
            self.driver.save_screenshot('login_error.png')
            print(f"❌ TEST FAILED: {str(e)}")
            self.__class__.test_results['test_2'] = f"Failed - {str(e)}"
            raise

    def test_3_edit_profile(self):
        print("\n🧪 TEST CASE 3: Edit Profile")
        try:
            self.test_2_successful_login()
            
            print("\nStep 2: Navigating to profile page...")
            profile_button = self.driver.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Profile"))
            )
            profile_button.click()
            
            print("\nStep 3: Updating profile fields...")
            # Use longer explicit waits
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.clear()
            username_input.send_keys("UpdatedUsername")
            
            name_input = self.driver.wait.until(EC.presence_of_element_located((By.NAME, "name")))
            name_input.clear()
            name_input.send_keys("Updated Name")
            
            email_input = self.driver.wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_input.clear()
            email_input.send_keys("updated@email.com")
            time.sleep(1)
            dob_input = self.driver.wait.until(EC.presence_of_element_located((By.NAME, "date_of_birth")))
            dob_input.clear()
            # dob_input.send_keys("9190-01-01")
            dob_input.send_keys("10-10-1991")
            time.sleep(1)
            save_button = self.driver.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            
            time.sleep(1)
            print("\nStep 4: Adding existing hobby...")
            hobby_input = self.driver.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='Type to search or add new hobby']")))
            hobby_input.send_keys("Reading")
            time.sleep(1)
            self.driver.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".list-group-item.list-group-item-action"))).click()
            
            print("\nStep 5: Adding new hobby...")
            hobby_input.clear()
            hobby_input.send_keys("Mountain Climbing")
            self.driver.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".btn.btn-outline-primary"))).click()
            
            print("\nStep 6: Updating password...")
            password_input = self.driver.wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_input.send_keys("newpassword123")
            
            print("\nStep 7: Saving changes...")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            time.sleep(1)
            save_button.click()
            time.sleep(2)
            
            print("Console logs after save:")
            console_logs = self.driver.get_log('browser')
            for log in console_logs:
                print(log['message'])
            
            time.sleep(1)
            alert = self.driver.switch_to.alert
            time.sleep(1)
            alert.accept()
            time.sleep(3)
            
            
            print("\nStep 8: Verifying updates...")
            # self.driver.refresh()
            # time.sleep(3)
            
            print("\nStep 8: Re-logging in after password change...")
            logout_button = self.driver.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-danger"))
            )
            logout_button.click()
            
            self.driver.get(f'{self.live_server_url}/api/login/')
            time.sleep(2)
        
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("UpdatedUsername")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys("newpassword123")
            self.driver.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
            time.sleep(2)
            
            profile_button = self.driver.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Profile"))
            )
            time.sleep(2)
            
            updated_user = CustomUser.objects.get(username='UpdatedUsername')
            # actual_dob = str(updated_user.date_of_birth)
            # expected_dob = "10-10-1991"        
            assert updated_user.name == "Updated Name", "❌ Name update failed"
            assert updated_user.email == "updated@email.com", "❌ Email update failed"
            assert str(updated_user.date_of_birth) == "1991-10-10", "❌ Date of birth update failed"
            assert any(h.hobby_name == "Reading" for h in updated_user.hobbies.all()), "❌ Existing hobby not added"
            assert any(h.hobby_name == "Mountain Climbing" for h in updated_user.hobbies.all()), "❌ New hobby not created"
            
            print("✅ TEST PASSED: Profile updated successfully")
            self.__class__.test_results['test_3'] = "Profile updated successfully with all fields changed"
            
        except Exception as e:
            print(f"❌ TEST FAILED: {str(e)}")
            self.__class__.test_results['test_3'] = f"Failed to update profile: {str(e)}"
            raise
    
    
    

    def test_4_filter_users(self):
        
        print("\n🧪 TEST CASE 4: Filter Users")
        print("-------------------------")
        try:
            # First login
            print("Step 1: Logging in...")
            self.test_2_successful_login()
            
            print("\nStep 2: Navigating to users page...")
            self.driver.get(f'{self.live_server_url}')
            time.sleep(1)
            
            old_user_cards = self.driver.find_elements(By.CSS_SELECTOR, ".card")
            
            print("\nStep 3: Checking pagination...")
            next_page= self.driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[name='nextPage']")))
            next_page.click()
            time.sleep(2)
            previous_page = self.driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[name='previousPage']")))
            previous_page.click()
            time.sleep(1)
            
            print("\nStep 4: Setting age filter...")
            min_age_input = self.driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='minAge']")))
            min_age_input.clear()
            min_age_input.send_keys("2")
            min_age_input.send_keys("5")
            min_age_input.send_keys(Keys.ENTER)
            
            # Add explicit wait for filter to be applied
            time.sleep(7)
            
            max_age_input = self.driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='maxAge']")))
            max_age_input.clear()
            max_age_input.send_keys("2")
            max_age_input.send_keys("9")
            max_age_input.send_keys(Keys.ENTER)
            
            
            
            print("\nStep 5: Verifying filtered results...")
            # Wait for user cards to be updated after filter
            self.driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card")))
            new_user_cards = self.driver.find_elements(By.CSS_SELECTOR, ".card")
            assert len(new_user_cards) < len(old_user_cards), "❌ No users displayed after filtering"
            print("✅ TEST PASSED: Age filtering works")
            self.__class__.test_results['test_4'] = "Age filter applied successfully - Result list updated with filtered users"
            
        except Exception as e:
            self.driver.save_screenshot('filter_users_error.png')
            print(f"❌ TEST FAILED: {str(e)}")
            self.__class__.test_results['test_4'] = f"Failed to apply age filter - Could not filter or display results: {str(e)}"
            raise

    def test_5_send_friend_request(self):
        print("\n🧪 TEST CASE 5: Send Friend Request")
        print("--------------------------------")
        try:
            # Login as testuser
            print("Step 1: Logging in as testuser...")
            self.driver.get(f'{self.live_server_url}/api/login/')
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("testuser")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys("testpass123")
            self.driver.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
            time.sleep(1)

            # Navigate to main page where user cards are displayed
            print("Step 2: Navigating to main page...")
            self.driver.get(f'{self.live_server_url}')
            time.sleep(1)

            # Find testuser2's card and send friend request
            print("Step 3: Finding testuser2's card and sending friend request...")
            # Wait for cards to load
            self.driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card")))
            
            # Find all cards
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".card")
            
            # Find testuser2's card
            testuser2_card = None
            for card in cards:
                try:
                    name_element = card.find_element(By.CSS_SELECTOR, ".card-title")
                    if "Test User 2" in name_element.text:  # This should match self.test_user2.name
                        testuser2_card = card
                        break
                except:
                    continue
                    
            assert testuser2_card is not None, "❌ Could not find testuser2's card"
            
            # Find and click the Send Friend Request button in testuser2's card
            send_request_button = testuser2_card.find_element(By.CSS_SELECTOR, "button.btn.btn-primary")
            send_request_button.click()
            time.sleep(1)

            # Verify friend request is pending
            print("Step 4: Verifying request was sent...")
            request_pending = testuser2_card.find_element(By.CSS_SELECTOR, "button.btn.btn-secondary[disabled]")
            assert "Request Pending" in request_pending.text, "❌ Friend request not sent"
            print("✅ TEST PASSED: Friend request sent successfully")
            self.__class__.test_results['test_5'] = "Friend request sent to Test User 2 - Status shows as pending"

        except Exception as e:
            self.driver.save_screenshot('friend_request_error.png')
            print(f"❌ TEST FAILED: {str(e)}")
            self.__class__.test_results['test_5'] = f"Failed to send friend request - Request could not be created: {str(e)}"
            raise

    def test_6_accept_friend_request(self):
        print("\n🧪 TEST CASE 6: Accept Friend Request")
        print("----------------------------------")
        try:
            # First ensure test_5 has run to create the friend request
            self.test_5_send_friend_request()
            
            # Logout first user
            print("Step 1: Logging out testuser...")
            self.driver.get(f"{self.live_server_url}/")
            logout_button = self.driver.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-danger")))
            logout_button.click()
            time.sleep(1)

            # Login as testuser2
            print("Step 2: Logging in as testuser2...")
            self.driver.get(f"{self.live_server_url}/api/login/")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("testuser2")
            self.driver.wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys("testpass123")
            self.driver.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
            time.sleep(1)

            # Navigate to main page where friend requests are shown
            print("Step 3: Checking friend requests...")
            self.driver.get(f"{self.live_server_url}/")
            
            # Look for friend request in the right column
            print("Step 4: Finding and accepting friend request...")
            # Wait for load
            friend_request = self.driver.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".card-header")))
            
            # Find and click accept button
            accept_button = self.driver.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-success.btn-sm")))
            accept_button.click()
            time.sleep(1)

            # Verify friend request was accepted by checking friends list
            print("Step 5: Verifying friend status...")
            # Wait for load
            self.driver.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".card-header")))
            
            # Find all friend cards
            friend_elements = self.driver.find_elements(By.CSS_SELECTOR, ".card-body .p-3.border.rounded h6")
            
            # Check if testuser is now in friends list
            found_friend = False
            for element in friend_elements:
                if "Test User" in element.text:  # This should match self.test_user.name
                    found_friend = True
                    
                    break
                    
            assert found_friend, "❌ Friend was not added to friends list"
            print("✅ TEST PASSED: Friend request accepted successfully")
            self.__class__.test_results['test_6'] = "Friend request accepted - Users appear in each other's friend lists"
            time.sleep(1)
            

        except Exception as e:
            self.driver.save_screenshot('accept_friend_request_error.png')
            print(f"❌ TEST FAILED: {str(e)}")
            self.__class__.test_results['test_6'] = f"Failed to accept friend request - Could not update friendship status: {str(e)}"
            raise


AuthenticationTests()