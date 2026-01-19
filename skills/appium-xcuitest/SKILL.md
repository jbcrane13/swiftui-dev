---
name: appium-xcuitest
description: iOS UI automation testing with Appium and XCUITest. Use when writing UI tests, creating page objects, locating elements by accessibility ID, implementing gestures, or setting up test automation infrastructure. Covers element location strategies, wait patterns, test organization, and CI/CD integration.
---

# Appium XCUITest Automation

iOS UI test automation using Appium with XCUITest driver.

**Scripts location**: `$CLAUDE_PLUGIN_ROOT/skills/appium-xcuitest/scripts/`

## Element Location Strategies

### Accessibility ID (Preferred)
**Always use accessibility identifiers - fastest and most reliable.**

```python
# Python
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login_button_submit")

# Pattern: {screen}_{element}_{descriptor}
# Examples:
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login_textfield_email")
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "settings_toggle_notifications")
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "home_cell_item_123")
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "screen_login")  # Screen container
```

### iOS Predicate String
```python
# Single attribute
element = driver.find_element(AppiumBy.IOS_PREDICATE, 'name == "Submit"')
element = driver.find_element(AppiumBy.IOS_PREDICATE, 'label CONTAINS "Welcome"')
element = driver.find_element(AppiumBy.IOS_PREDICATE, 'value BEGINSWITH "Search"')

# Multiple attributes
element = driver.find_element(
    AppiumBy.IOS_PREDICATE,
    'type == "XCUIElementTypeButton" AND name == "Submit"'
)

# Enabled/visible state
element = driver.find_element(
    AppiumBy.IOS_PREDICATE,
    'enabled == true AND visible == true AND name == "login_button_submit"'
)
```

### iOS Class Chain
```python
# Direct child
element = driver.find_element(
    AppiumBy.IOS_CLASS_CHAIN,
    '**/XCUIElementTypeButton[`name == "Submit"`]'
)

# Nested hierarchy
element = driver.find_element(
    AppiumBy.IOS_CLASS_CHAIN,
    '**/XCUIElementTypeCell[`name CONTAINS "item"`]/XCUIElementTypeButton'
)

# Index-based (use sparingly)
element = driver.find_element(
    AppiumBy.IOS_CLASS_CHAIN,
    '**/XCUIElementTypeTable/XCUIElementTypeCell[3]'
)
```

## Page Object Pattern

```python
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    """Page object for login screen."""

    # Locators - all using accessibility IDs
    EMAIL_FIELD = (AppiumBy.ACCESSIBILITY_ID, "login_textfield_email")
    PASSWORD_FIELD = (AppiumBy.ACCESSIBILITY_ID, "login_textfield_password")
    SUBMIT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "login_button_submit")
    ERROR_LABEL = (AppiumBy.ACCESSIBILITY_ID, "login_label_error")
    SCREEN = (AppiumBy.ACCESSIBILITY_ID, "screen_login")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def is_displayed(self) -> bool:
        """Check if login screen is displayed."""
        try:
            self.wait.until(EC.presence_of_element_located(self.SCREEN))
            return True
        except:
            return False

    def enter_email(self, email: str):
        """Enter email address."""
        element = self.wait.until(EC.element_to_be_clickable(self.EMAIL_FIELD))
        element.clear()
        element.send_keys(email)
        return self

    def enter_password(self, password: str):
        """Enter password."""
        element = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_FIELD))
        element.clear()
        element.send_keys(password)
        return self

    def tap_submit(self):
        """Tap submit button."""
        element = self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BUTTON))
        element.click()
        return HomePage(self.driver)  # Return next page

    def login(self, email: str, password: str):
        """Complete login flow."""
        return self.enter_email(email).enter_password(password).tap_submit()

    def get_error_message(self) -> str:
        """Get error message if displayed."""
        element = self.wait.until(EC.visibility_of_element_located(self.ERROR_LABEL))
        return element.text
```

## Wait Patterns

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)

# Wait for element present
element = wait.until(EC.presence_of_element_located(
    (AppiumBy.ACCESSIBILITY_ID, "home_list_items")
))

# Wait for element clickable
element = wait.until(EC.element_to_be_clickable(
    (AppiumBy.ACCESSIBILITY_ID, "home_button_add")
))

# Wait for element visible
element = wait.until(EC.visibility_of_element_located(
    (AppiumBy.ACCESSIBILITY_ID, "dialog_message")
))

# Wait for element to disappear
wait.until(EC.invisibility_of_element_located(
    (AppiumBy.ACCESSIBILITY_ID, "loading_indicator")
))

# Custom wait condition
def element_has_text(locator, text):
    def _predicate(driver):
        element = driver.find_element(*locator)
        return element.text == text
    return _predicate

wait.until(element_has_text(
    (AppiumBy.ACCESSIBILITY_ID, "status_label"),
    "Complete"
))
```

## Gesture Actions

```python
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction

# Tap
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "button_action")
element.click()

# Long press
action = TouchAction(driver)
action.long_press(element, duration=1000).release().perform()

# Swipe (coordinates)
driver.swipe(start_x=200, start_y=500, end_x=200, end_y=100, duration=500)

# Swipe on element
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "list_container")
driver.execute_script('mobile: swipe', {
    'direction': 'up',
    'element': element
})

# Scroll to element
driver.execute_script('mobile: scroll', {
    'direction': 'down',
    'predicateString': 'name == "target_element"'
})

# Pinch/Zoom
driver.execute_script('mobile: pinch', {
    'scale': 0.5,  # < 1 pinch in, > 1 pinch out
    'velocity': 1.0
})
```

## Test Organization

```python
import pytest
from appium import webdriver

class TestLogin:
    """Login feature tests."""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        """Setup before each test."""
        self.driver = driver
        self.login_page = LoginPage(driver)
        # Navigate to login if needed

    def test_successful_login(self):
        """Test valid credentials login."""
        home_page = self.login_page.login("user@example.com", "password123")
        assert home_page.is_displayed()

    def test_invalid_email_error(self):
        """Test error for invalid email format."""
        self.login_page.enter_email("invalid").tap_submit()
        assert "valid email" in self.login_page.get_error_message().lower()

    def test_empty_password_error(self):
        """Test error for empty password."""
        self.login_page.enter_email("user@example.com").tap_submit()
        assert "password" in self.login_page.get_error_message().lower()
```

## Capabilities Configuration

```python
caps = {
    # Platform
    "platformName": "iOS",
    "platformVersion": "18.0",
    "deviceName": "iPhone 16 Pro",

    # App
    "app": "/path/to/MyApp.app",
    "bundleId": "com.example.myapp",

    # Automation
    "automationName": "XCUITest",
    "noReset": False,
    "fullReset": False,

    # Timeouts
    "newCommandTimeout": 300,
    "wdaLaunchTimeout": 120000,
    "wdaConnectionTimeout": 120000,

    # Performance
    "usePrebuiltWDA": True,
    "derivedDataPath": "/path/to/DerivedData",

    # Debugging
    "showXcodeLog": True,
    "showIOSLog": True,
}

driver = webdriver.Remote("http://localhost:4723", caps)
```

## Script Utilities

### Generate Page Object
```bash
python $CLAUDE_PLUGIN_ROOT/skills/appium-xcuitest/scripts/gen_page_object.py LoginPage \
    --elements "email:textfield,password:textfield,submit:button,error:label" \
    --output ./tests/pages/
```

### Extract Accessibility IDs from App
```bash
python $CLAUDE_PLUGIN_ROOT/skills/appium-xcuitest/scripts/extract_ids.py \
    --app ./build/MyApp.app \
    --output ./accessibility_ids.json
```

## Best Practices

1. **Always use accessibility IDs** - Fastest and most reliable locator strategy
2. **Follow naming convention** - `{screen}_{element}_{descriptor}`
3. **Use page objects** - Encapsulate screen logic for maintainability
4. **Implement proper waits** - Never use sleep(), use explicit waits
5. **Keep tests independent** - Each test should be able to run in isolation
6. **Use screen identifiers** - Add `screen_{name}` to verify navigation
7. **Handle alerts** - Always check for and dismiss system alerts

## Detailed References

- **Locator Strategies**: See [references/locators.md](references/locators.md)
- **Gestures**: See [references/gestures.md](references/gestures.md)
- **CI/CD Integration**: See [references/ci-cd.md](references/ci-cd.md)
- **Troubleshooting**: See [references/troubleshooting.md](references/troubleshooting.md)
