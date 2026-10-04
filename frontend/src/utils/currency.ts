export const formatCurrency = (amount: number | string | undefined | null): string => {
    if (amount === undefined || amount === null) return 'Rs 0.00';
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    if (isNaN(num)) return 'Rs 0.00';
    
    // Using PKR (Pakistani Rupee) formatting by default as requested
    return new Intl.NumberFormat('en-PK', {
        style: 'currency',
        currency: 'PKR',
        minimumFractionDigits: 2
    }).format(num);
};
