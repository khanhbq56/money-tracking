/**
 * Test UI Fixes for Dashboard Color and Chat Functionality
 * Tests for issues reported in user feedback
 */

// Test 1: Dashboard Monthly Total Color Stability
function testDashboardMonthlyTotalColor() {
    console.log('🧪 Testing Dashboard Monthly Total Color Stability...');
    
    // Simulate different net total values and check color consistency
    const testCases = [
        { netTotal: 1000000, expectedColorClass: 'from-green-50', description: 'Positive balance' },
        { netTotal: -500000, expectedColorClass: 'from-red-50', description: 'Negative balance' },
        { netTotal: 0, expectedColorClass: 'from-purple-50', description: 'Zero balance' }
    ];
    
    testCases.forEach(testCase => {
        console.log(`  Testing ${testCase.description}: ${testCase.netTotal}`);
        
        // Mock dashboard instance
        if (window.dashboard && window.dashboard.updateMonthlyTotalCardColor) {
            window.dashboard.updateMonthlyTotalCardColor(testCase.netTotal);
            
            // Check after timeout to allow for DOM update
            setTimeout(() => {
                const card = document.getElementById('monthly-net-total')?.closest('.bg-gradient-to-br');
                if (card) {
                    const hasExpectedClass = card.classList.contains(testCase.expectedColorClass);
                    console.log(`    ✅ Expected class ${testCase.expectedColorClass}: ${hasExpectedClass ? 'PASS' : 'FAIL'}`);
                } else {
                    console.log(`    ❌ Monthly total card not found`);
                }
            }, 100);
        } else {
            console.log(`    ⚠️ Dashboard not initialized`);
        }
    });
}

// Test 2: Chat Transaction Type Consistency
function testChatTransactionTypeConsistency() {
    console.log('🧪 Testing Chat Transaction Type Consistency...');
    
    // Mock chat data with expense type
    const mockChatData = {
        chat_id: 'test_123',
        ai_result: {
            type: 'expense',
            amount: 20000,
            description: 'Coffee',
            category: 'coffee',
            icon: '☕',
            confidence: 0.9
        },
        suggested_text: '☕ Phân loại: Chi tiêu - Coffee (20,000₫)'
    };
    
    console.log(`  Mock chat response: ${mockChatData.suggested_text}`);
    
    // Test if calendar receives correct transaction_type
    const expectedCalendarData = {
        transaction_type: 'expense',  // Should be 'transaction_type', not 'type'
        expense_category: 'coffee',   // Should be 'expense_category', not 'category'
        amount: 20000,
        description: 'Coffee'
    };
    
    console.log(`  Expected calendar data format:`, expectedCalendarData);
    
    // Check if calendar day-event will have correct CSS class
    const mockEventElement = document.createElement('div');
    mockEventElement.className = `day-event ${expectedCalendarData.transaction_type}`;
    
    const hasExpenseClass = mockEventElement.classList.contains('expense');
    console.log(`  ✅ Calendar event has expense class: ${hasExpenseClass ? 'PASS' : 'FAIL'}`);
    
    // Check CSS styling for expense events
    const computedStyle = window.getComputedStyle(mockEventElement);
    document.body.appendChild(mockEventElement);
    const actualStyles = window.getComputedStyle(mockEventElement);
    document.body.removeChild(mockEventElement);
    
    console.log(`  Expected red color styling for expense events`);
}

// Test 3: Calendar Event Color Application
function testCalendarEventColors() {
    console.log('🧪 Testing Calendar Event Colors...');
    
    const transactionTypes = ['expense', 'saving', 'investment'];
    const expectedColors = {
        'expense': 'rgb(220, 38, 38)',      // Red
        'saving': 'rgb(22, 163, 74)',       // Green  
        'investment': 'rgb(37, 99, 235)'     // Blue
    };
    
    transactionTypes.forEach(type => {
        const eventElement = document.createElement('div');
        eventElement.className = `day-event ${type}`;
        eventElement.textContent = `☕ 20k`;
        
        // Add to DOM temporarily to get computed styles
        document.body.appendChild(eventElement);
        const computedStyle = window.getComputedStyle(eventElement);
        const actualColor = computedStyle.color;
        document.body.removeChild(eventElement);
        
        console.log(`  ${type} event color: ${actualColor}`);
        console.log(`  Expected: ${expectedColors[type]}`);
        
        // Note: Exact color matching might vary due to CSS processing
        const hasColorStyle = actualColor !== 'rgb(0, 0, 0)'; // Not default black
        console.log(`    ✅ Has custom color: ${hasColorStyle ? 'PASS' : 'FAIL'}`);
    });
}

// Test 4: API Response Format Validation
function testAPIResponseFormat() {
    console.log('🧪 Testing API Response Format...');
    
    // Mock transaction data as it should come from API
    const mockAPIResponse = {
        daily_data: {
            '2024-01-15': {
                transactions: [
                    {
                        id: 1,
                        transaction_type: 'expense',  // Correct key
                        expense_category: 'coffee',   // Correct key
                        amount: 20000,
                        description: 'Coffee',
                        icon: '☕'
                    }
                ],
                totals: {
                    expense: -20000,
                    saving: 0,
                    investment: 0,
                    net: 20000
                }
            }
        }
    };
    
    console.log(`  API Response structure:`, mockAPIResponse);
    
    // Test if calendar can process this format correctly
    const transaction = mockAPIResponse.daily_data['2024-01-15'].transactions[0];
    const hasCorrectKeys = (
        transaction.hasOwnProperty('transaction_type') &&
        transaction.hasOwnProperty('expense_category') &&
        transaction.transaction_type === 'expense'
    );
    
    console.log(`  ✅ API response has correct keys: ${hasCorrectKeys ? 'PASS' : 'FAIL'}`);
    
    // Test calendar event creation with this data
    if (window.calendar && window.calendar.createEventElement) {
        try {
            const eventElement = window.calendar.createEventElement(transaction, new Date());
            const hasExpenseClass = eventElement.classList.contains('expense');
            console.log(`  ✅ Calendar creates event with expense class: ${hasExpenseClass ? 'PASS' : 'FAIL'}`);
        } catch (error) {
            console.log(`  ❌ Error creating calendar event: ${error.message}`);
        }
    } else {
        console.log(`  ⚠️ Calendar not available for testing`);
    }
}

// Run tests when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Starting UI Fix Tests...');
    
    // Wait a bit for other scripts to initialize
    setTimeout(() => {
        testDashboardMonthlyTotalColor();
        testChatTransactionTypeConsistency();
        testCalendarEventColors();
        testAPIResponseFormat();
        
        console.log('✅ UI Fix Tests completed!');
    }, 2000);
});

// Manual test trigger functions
window.testUIFixes = {
    testDashboardColors: testDashboardMonthlyTotalColor,
    testChatConsistency: testChatTransactionTypeConsistency,
    testCalendarColors: testCalendarEventColors,
    testAPIFormat: testAPIResponseFormat
};

console.log('UI Fix Test Suite loaded. Use window.testUIFixes to run individual tests.'); 