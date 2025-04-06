// Format angka ke mata uang Rupiah
function formatCurrency(value) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Parse input user ke bentuk float
function parseCurrency(input) {
    // Hapus karakter non-digit kecuali koma
    let cleanValue = input.replace(/[^\d,]/g, '');

    // Pisahkan bagian integer dan desimal
    let [integerPart, decimalPart] = cleanValue.split(',');

    // Hapus titik pemisah ribuan
    integerPart = integerPart.replace(/\./g, '');

    // Pastikan bagian desimal ada dan panjangnya 2 digit
    decimalPart = (decimalPart || '00').padEnd(2, '0').substring(0,2);

    return parseFloat(`${integerPart}.${decimalPart}`).toFixed(4);
}
