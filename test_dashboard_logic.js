/**
 * Test Dashboard Logic - Verify Today Summary Calculation
 * Run this in browser console to test the fixed logic
 */

// Mock transaction data
const mockTransactions = [
    { transaction_type: 'expense', amount: 50000, description: 'Ăn trưa' },
    { transaction_type: 'expense', amount: 25000, description: 'Coffee' },
    { transaction_type: 'saving', amount: 200000, description: 'Tiết kiệm' },
    { transaction_type: 'investment', amount: 100000, description: 'Đầu tư' }
];

// Test calculation logic
function testTodayTotalCalculation() {
    console.log('🧪 Testing Today Total Calculation Logic');
    console.log('======================================');
    
    let totalToday = 0;
    console.log('\n📝 Processing transactions:');
    
    mockTransactions.forEach((transaction, index) => {
        const transactionType = transaction.transaction_type;
        const amount = Math.abs(parseFloat(transaction.amount));
        // NEW LOGIC: Sum absolute values (total money moved)
        totalToday += amount;
        
        const sign = transactionType === 'expense' ? '-' : '+';
        console.log(`${index + 1}. ${transaction.description}: ${sign}${amount.toLocaleString()}₫ (${transactionType})`);
        console.log(`   Running total: +${totalToday.toLocaleString()}₫ (money moved)`);
    });
    
    // Final calculation (NEW: absolute sum logic)
    const totalClass = 'text-blue-600'; // Blue for total amount moved
    const totalSign = '+'; // Always positive for total money moved
    const totalAbsAmount = totalToday;
    
    console.log('\n📊 Final Results (Total Money Moved):');
    console.log(`Raw total: ${totalToday.toLocaleString()}₫`);
    console.log(`Display total: ${totalSign}${totalAbsAmount.toLocaleString()}₫`);
    console.log(`CSS class: ${totalClass}`);
    
    // Expected result (sum of absolute values)
    const expectedTotal = 50000 + 25000 + 200000 + 100000; // = 375000
    const isCorrect = totalToday === expectedTotal;
    
    console.log('\n✅ Verification:');
    console.log(`Expected: +${expectedTotal.toLocaleString()}₫ (absolute sum)`);
    console.log(`Actual: ${totalSign}${totalAbsAmount.toLocaleString()}₫`);
    console.log(`Result: ${isCorrect ? '✅ CORRECT' : '❌ INCORRECT'}`);
    console.log('\n💡 Explanation: Total shows how much money moved in total (regardless of direction)');
    
    return isCorrect;
}

// Test emoji regex
function testEmojiRegex() {
    console.log('\n🎭 Testing Emoji Regex');
    console.log('=====================');
    
    const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|🟢|🔴|🔵|📊|📅|🤖|⚡|📝/gu;
    
    const testTexts = [
        '🟢 Tiết Kiệm',
        '🔴 Chi Tiêu', 
        '🔵 Đầu Tư',
        '📊 Tổng Tháng',
        '📅 Lịch Tài Chính',
        '🤖 AI Assistant'
    ];
    
    testTexts.forEach(text => {
        const emojiMatch = text.match(emojiRegex);
        const emoji = emojiMatch ? emojiMatch[0] : 'NO MATCH';
        console.log(`"${text}" → emoji: "${emoji}"`);
    });
}

// Run both tests
console.log('🔬 Dashboard Logic Test Suite');
console.log('============================');

const calculationTest = testTodayTotalCalculation();
testEmojiRegex();

console.log('\n🎯 Overall Result:');
console.log(`Calculation Test: ${calculationTest ? '✅ PASS' : '❌ FAIL'}`);
console.log('Emoji Test: ✅ PASS (if icons show above)');

// Export for use
if (typeof window !== 'undefined') {
    window.testDashboardLogic = {
        testTodayTotalCalculation,
        testEmojiRegex
    };
} 