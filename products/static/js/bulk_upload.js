// RANT: FUCKK, THIS TOO 
// Im a bit stressed here -,-'
//TOo many hacky ways here  !!!

//For me in the future
//BE A BETTER CODER AND PROGRAMMER !!!

let previewData = [];
let previewHeaders = [];
let previewTable = null;

// Utility function to wait for libraries to load
function waitForLibraries() {
    return new Promise((resolve, reject) => {
        let attempts = 0;
        const maxAttempts = 50;
        
        const checkLibraries = () => {
            attempts++;
            
            if (typeof jQuery === 'undefined') {
                if (attempts >= maxAttempts) {
                    reject('jQuery failed to load');
                    return;
                }
                setTimeout(checkLibraries, 100);
                return;
            }
            
            if (typeof $.fn.DataTable === 'undefined') {
                if (attempts >= maxAttempts) {
                    reject('DataTables failed to load');
                    return;
                }
                setTimeout(checkLibraries, 100);
                return;
            }
            
            resolve();
        };
        
        checkLibraries();
    });
}

// Initialize when libraries are ready
waitForLibraries().then(() => {
    initializeApp();
}).catch((error) => {
    console.error('Library loading error:', error);
    Swal.fire('Error', `Gagal memuat library: ${error}. Silakan refresh halaman.`, 'error');
});

function initializeApp() {
    $(document).ready(function() {
        // File upload drag and drop
        setupDragDrop();
        
        // Handle form upload
        $('#upload-form').on('submit', function(e) {
            e.preventDefault();
            handleFileUpload();
        });

        // Reset preview
        $('#reset-btn').on('click', function() {
            resetPreview();
        });

        // Apply data ke database
        $('#apply-btn').on('click', function() {
            applyDataToDatabase();
        });

        // Edit again button (enable re-edit mode)
        $('#edit-again-btn').on('click', function() {
            previewData.forEach(row => { row['Status'] = 'Belum Diproses'; });
            renderPreviewTable();
            $('#apply-btn').prop('disabled', false);
            $('#edit-again-btn').addClass('d-none');
            Swal.fire('Edit Mode', 'Anda dapat mengedit dan apply ulang data.', 'info');
        });
    });
}

function setupDragDrop() {
    const uploadArea = $('#upload-area');
    const fileInput = $('#excelFile');
    
    uploadArea.on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('dragover');
    });
    
    uploadArea.on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
    });
    
    uploadArea.on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
        
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            fileInput[0].files = files;
            handleFileUpload();
        }
    });
}

function handleFileUpload() {
    // Reset all preview state before processing new file
    previewData = [];
    previewHeaders = [];
    if (previewTable) {
        previewTable.destroy();
        previewTable = null;
    }
    $('#preview-table').empty();
    $('#preview-section').hide();
    $('#data-stats').empty();
    $('#apply-btn').prop('disabled', false);
    $('#edit-again-btn').addClass('d-none');

    let fileInput = $('#excelFile')[0];
    if (!fileInput.files.length) {
        Swal.fire('Pilih file', 'Silakan pilih file Excel terlebih dahulu', 'warning');
        return;
    }
    
    const file = fileInput.files[0];
    if (!file.name.endsWith('.xlsx')) {
        Swal.fire('Format file salah', 'Hanya file .xlsx yang diperbolehkan', 'error');
        return;
    }
    
    let formData = new FormData();
    formData.append('excelFile', file);
    
    // Show loading
    Swal.fire({
        title: 'Memproses...',
        text: 'Sedang memproses file Excel',
        allowOutsideClick: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    $.ajax({
        url: '/products/preview_bulk_upload',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        timeout: 30000, // 30 second timeout
        success: function(resp) {
            Swal.close();
            if (resp.success) {
                previewData = resp.data || [];
                previewHeaders = resp.headers || [];
                
                if (previewData.length === 0) {
                    Swal.fire('Tidak ada data', 'File Excel tidak mengandung data yang valid', 'warning');
                    return;
                }
                
                renderPreviewTable();
                $('#preview-section').show();
                
                // Scroll to preview section
                $('html, body').animate({
                    scrollTop: $("#preview-section").offset().top - 50
                }, 500);
                
            } else {
                Swal.fire('Error', resp.message || 'Gagal memproses file', 'error');
            }
        },
        error: function(xhr, status, error) {
            Swal.close();
            let errorMsg = 'Gagal upload file';
            
            if (status === 'timeout') {
                errorMsg = 'Upload timeout. File terlalu besar atau koneksi lambat.';
            } else if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMsg = xhr.responseJSON.message;
            } else if (xhr.status === 0) {
                errorMsg = 'Tidak dapat terhubung ke server. Periksa koneksi internet.';
            } else if (xhr.status === 413) {
                errorMsg = 'File terlalu besar. Maksimal ukuran file adalah 10MB.';
            }
            
            Swal.fire('Error', errorMsg, 'error');
        }
    });
}

function resetPreview() {
    previewData = [];
    previewHeaders = [];
    
    if (previewTable) {
        previewTable.destroy();
        previewTable = null;
    }
    
    $('#preview-table').empty();
    $('#preview-section').hide();
    $('#excelFile').val('');
    $('#data-stats').empty();
}

function applyDataToDatabase() {
    if (!previewData.length) {
        Swal.fire('Tidak ada data', 'Tidak ada data yang akan diinputkan', 'warning');
        return;
    }
    
    $('#apply-btn').prop('disabled', true);
    
    Swal.fire({
        title: 'Konfirmasi',
        html: `Akan memasukkan <strong>${previewData.length}</strong> item ke database.<br>Lanjutkan?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Ya, Apply',
        cancelButtonText: 'Batal',
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: 'Memproses...',
                text: 'Sedang menyimpan data ke database',
                allowOutsideClick: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            
            $.ajax({
                url: '/products/apply_bulk_upload',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({items: previewData}),
                timeout: 60000, // 60 second timeout
                success: function(resp) {
                    Swal.close();
                    if (resp.success) {
                        // Update status per baris dari backend jika tersedia
                        if (resp.statuses && resp.statuses.length > 0) {
                            resp.statuses.forEach((stat, i) => {
                                if (previewData[i]) {
                                    previewData[i]['Status'] = stat;
                                }
                            });
                        } else {
                            // Jika tidak ada status detail, update berdasarkan hasil umum
                            previewData.forEach((row, i) => {
                                if (i < (resp.inserted || 0)) {
                                    row['Status'] = 'Berhasil Input';
                                } else if (i < ((resp.inserted || 0) + (resp.updated || 0))) {
                                    row['Status'] = 'Update';
                                } else {
                                    row['Status'] = 'Gagal';
                                }
                            });
                        }
                        
                        // Re-render table dengan status terbaru
                        renderPreviewTable();
                        $('#edit-again-btn').removeClass('d-none');
                        $('#apply-btn').prop('disabled', true);
                        
                        let message = `<div class="text-left">`;
                        message += `<strong>Proses berhasil!</strong><br>`;
                        message += `✅ Barang baru: ${resp.inserted || 0}<br>`;
                        message += `🔄 Update: ${resp.updated || 0}<br>`;
                        message += `❌ Gagal: ${resp.failed || 0}`;
                        message += `</div>`;
                        
                        Swal.fire({
                            title: 'Sukses',
                            html: message,
                            icon: 'success',
                            confirmButtonText: 'OK'
                        });
                    } else {
                        Swal.fire('Error', resp.message || 'Gagal menyimpan data', 'error');
                        $('#apply-btn').prop('disabled', false);
                    }
                },
                error: function(xhr, status, error) {
                    Swal.close();
                    let errorMsg = 'Gagal apply data';
                    if (status === 'timeout') {
                        errorMsg = 'Proses timeout. Data terlalu banyak atau server sibuk.';
                    } else if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMsg = xhr.responseJSON.message;
                    }
                    Swal.fire('Error', errorMsg, 'error');
                    $('#apply-btn').prop('disabled', false);
                }
            });
        } else {
            $('#apply-btn').prop('disabled', false);
        }
    });
}

function updateDataStats() {
    const totalRows = previewData.length;
    $('#data-stats').html(`
        <span class="stats-badge">${totalRows} Baris Data</span>
        <span class="stats-badge">${previewHeaders.length} Kolom</span>
    `);
}

function renderPreviewTable() {
    // Tambahkan kolom status jika belum ada
    if (!previewHeaders.includes('Status')) {
        previewHeaders.push('Status');
        previewData.forEach(row => { row['Status'] = row['Status'] || 'Belum Diproses'; });
    }
    
    // Destroy existing table
    if (previewTable) {
        try {
            previewTable.destroy();
        } catch (e) {
            console.warn('Error destroying table:', e);
        }
        previewTable = null;
    }
    
    // Update stats
    updateDataStats();
    
    // Build table header
    let thead = `
        <thead>
            <tr>
                ${previewHeaders.map(header => 
                    `<th>${header}</th>`
                ).join('')}
                <th class="text-center">Aksi</th>
            </tr>
        </thead>`;

    // Build table body
    let tbody = '<tbody>';
    previewData.forEach((row, idx) => {
        // Pastikan setiap baris memiliki UID stabil
        if (!row.uid) row.uid = row.uid || (Date.now().toString(36) + Math.random().toString(36).substr(2, 5));
        tbody += `<tr data-idx="${idx}" data-uid="${row.uid}">`;
        previewHeaders.forEach(h => {
            let value = row[h] !== null && row[h] !== undefined ? String(row[h]) : '';
            console.log(h);
            if (h === 'Status') {
                // Badge warna sesuai status
                let badgeClass = 'bg-secondary';
                let badgeText = value;
                if (value === 'Berhasil Input' || value === 'Berhasil') badgeClass = 'bg-success';
                else if (value === 'Update' || value === 'Updated') badgeClass = 'bg-info';
                else if (value === 'Gagal' || value === 'Failed' || value === 'Error') badgeClass = 'bg-danger';
                else if (value === 'Belum Diproses') badgeClass = 'bg-secondary';
                tbody += `<td class="text-center"><span class="badge ${badgeClass}">${badgeText}</span></td>`;
            } else if (h.toLowerCase().replace(/[^a-z]/g,'').includes('kadaluarsa')) {
                console.log("Exscuted");
                // Kolom tanggal kadaluarsa dengan datepicker
                tbody += `<td class="datepicker-cell" data-row="${idx}" data-header="${h}">
                    <input type="date" class="datepicker-input form-control form-control-sm" value="${value}">
                </td>`;
            } else {
                tbody += `<td class="editable-cell" contenteditable="true" data-header="${h}" title="Klik untuk edit">${value}</td>`;
            }
        });
        tbody += `<td class="action-cell"><button class="btn btn-sm btn-danger btn-hapus" type="button" title="Hapus baris ini" data-uid="${row.uid}">Hapus</button></td>`;
        tbody += '</tr>';
    });
    tbody += '</tbody>';
    
    // Set table HTML
    $('#preview-table').html(thead + tbody);
    
    // Initialize DataTable with error handling
    try {
        // Add loading class
        $('#preview-table').addClass('table-loading');
        setTimeout(() => {
            // Pastikan kolom Aksi (kolom terakhir) tidak di-sort dan tidak di-search
            const columnDefs = [
                {
                    targets: previewHeaders.indexOf('Status'),
                    searchable: true,
                    orderable: true,
                    responsivePriority: 2,
                    render: function(data, type, row) {
                        return data; // Sudah dirender badge di HTML
                    }
                },
                {
                    targets: -1, // Target kolom terakhir (Aksi)
                    searchable: false,
                    orderable: false,
                    className: 'text-center',
                    responsivePriority: 1 // Selalu tampilkan kolom Aksi
                }
            ];

            // Beri prioritas tinggi untuk kolom yang mengandung "kadaluarsa"
            previewHeaders.forEach((hdr, hdrIdx) => {
                if (hdr.toLowerCase().replace(/[^a-z]/g,'').includes('kadaluarsa')) {
                    columnDefs.push({
                        targets: hdrIdx,
                        responsivePriority: 2,
                        className: 'text-center'
                    });
                }
            });

            previewTable = $('#preview-table').DataTable({
                scrollX: true,
                autoWidth: true,
                responsive: false,
                paging: true,
                searching: true,
                info: true,
                ordering: false,
                pageLength: 25,
                columnDefs: columnDefs,
                language: {
                    search: "Cari:",
                    lengthMenu: "Tampilkan _MENU_",
                    info: "Menampilkan _START_ sampai _END_ dari _TOTAL_ data",
                    infoEmpty: "Menampilkan 0 sampai 0 dari 0 data",
                    infoFiltered: "(difilter dari _MAX_ total data)",
                    paginate: {
                        first: "Pertama",
                        last: "Terakhir",
                        next: "Selanjutnya",
                        previous: "Sebelumnya"
                    },
                    emptyTable: "Tidak ada data yang tersedia",
                    processing: "Memproses..."
                },
                drawCallback: function() {
                    // Remove loading class when table is drawn
                    $('#preview-table').removeClass('table-loading');
                    bindTableEvents();
                },
                initComplete: function() {
                    // Patch: pastikan search bar selalu rata kanan setelah DataTable load
                    setTimeout(function() {
                        $('#preview-table_filter').css({
                            'margin-left': 'auto',
                            'margin-right': '0',
                            'text-align': 'right',
                            'display': 'block',
                            'width': 'auto',
                            'max-width': '400px'
                        });
                        // Responsive mobile
                        if (window.innerWidth <= 576) {
                            $('#preview-table_filter').css({
                                'width': '100%',
                                'margin-left': '0',
                                'text-align': 'center',
                                'max-width': '100%'
                            });
                            $('#preview-table_filter label').css('justify-content', 'center');
                        } else {
                            $('#preview-table_filter label').css('justify-content', 'flex-end');
                        }
                    }, 0);
                    // Tambahkan filter status otomatis hanya pada kolom Status
                    let statusIdx = previewHeaders.indexOf('Status');
                    if (statusIdx >= 0) {
                        // Dapatkan header kolom Status
                        let api = this.api();
                        let statusHeader = api.column(statusIdx).header();
                        
                        // Render teks header Status dan dropdown filter
                        // Layout: Status <icon filter>
                $(statusHeader).html('<span style="display:flex;align-items:center;justify-content:center;gap:4px;">Status <button type="button" class="btn btn-link p-0 m-0 status-filter-btn" title="Filter Status"><i class="fas fa-filter"></i></button></span>');

                // Custom dropdown filter
                if ($('#status-filter-dropdown-menu').length) $('#status-filter-dropdown-menu').remove();
                // Status mapping based on backend keys with user-friendly labels and icons
                const statusOptions = [
                    { key: '', label: 'Semua Status', icon: 'fas fa-list-ul text-secondary', color: '' },
                    { key: 'Belum Diproses', label: 'Belum Diproses', icon: 'fas fa-plus-circle text-secondary', color: 'text-secondary' },
                    { key: 'Berhasil Input', label: 'Berhasil Ditambah', icon: 'fas fa-plus-circle text-success', color: 'text-success' },
                    { key: 'Update', label: 'Berhasil Diupdate', icon: 'fas fa-sync-alt text-info', color: 'text-info' },
                    { key: 'Gagal', label: 'Gagal Diinput', icon: 'fas fa-times-circle text-danger', color: 'text-danger' }
                ];

                if ($('#status-filter-dropdown-menu').length) $('#status-filter-dropdown-menu').remove();
                const $dropdown = $('<div id="status-filter-dropdown-menu" class="dropdown-menu show" style="min-width:170px;position:absolute;z-index:1051;display:none;"></div>');
                statusOptions.forEach(opt => {
                    $dropdown.append(
                        `<button class="dropdown-item status-filter-item" data-status="${opt.key}">
                            <i class="${opt.icon} me-2"></i>${opt.label}
                        </button>`
                    );
                });
                $dropdown.appendTo('body');

                $(statusHeader).find('.status-filter-btn').off('click').on('click', function(e) {
                    e.stopPropagation();
                    const btnOffset = $(this).offset();
                    $dropdown.css({
                        top: btnOffset.top + $(this).outerHeight(),
                        left: btnOffset.left,
                        display: 'block'
                    });
                    // Close dropdown on outside click
                    $(document).one('click.statusfilter', function() { $dropdown.hide(); });
                });

                $dropdown.off('click').on('click', '.status-filter-item', function(e) {
                    e.preventDefault();
                    let val = $(this).data('status');
                    api.column(statusIdx).search(val ? '^'+val+'$' : '', true, false).draw();
                    $dropdown.hide();
                });
                            
                        // Recalculate responsive layout agar kolom Aksi tetap terlihat
                        api.columns.adjust().responsive.recalc();
                    }
                }
            });
        }, 100);
        
    } catch (error) {
        console.error('Error initializing DataTable:', error);
        $('#preview-table').removeClass('table-loading');
        Swal.fire('Error', 'Gagal membuat tabel. Periksa console untuk detail.', 'error');
    }
}

function bindTableEvents() {
    // Native date input: update previewData on change
    $('.datepicker-input').off('change').on('change', function() {
        const $cell = $(this).closest('.datepicker-cell');
        const rowIdx = $cell.data('row');
        const header = $cell.data('header');
        if (previewData[rowIdx]) {
            previewData[rowIdx][header] = $(this).val();
        }
    });
    // Handle delete button (event delegation)
    $(document).off('click', '.btn-hapus').on('click', '.btn-hapus', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        let uid = $(this).data('uid') || $(this).closest('tr').data('uid');
        let idx = previewData.findIndex(r => r.uid === uid);
        if (idx === -1) {
            Swal.fire('Error', 'Data tidak ditemukan', 'error');
            return;
        }
        let rowData = previewData[idx];
        let itemName = rowData[previewHeaders[0]] || 'Item'; // Ambil kolom pertama sebagai nama
        
        Swal.fire({
            title: 'Konfirmasi Hapus',
            html: `Yakin ingin menghapus baris ini?<br><strong>${itemName}</strong>`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Ya, Hapus',
            cancelButtonText: 'Batal',
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d'
        }).then((result) => {
            if (result.isConfirmed) {
                // Hapus data dari array
                previewData.splice(idx, 1);
                
                // Re-render table
                renderPreviewTable();
                
                Swal.fire({
                    title: 'Terhapus!',
                    text: 'Baris berhasil dihapus.',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                });
            }
        });
    });

    // Handle cell edit (event delegation)
    $(document).off('blur', '.editable-cell').on('blur', '.editable-cell', function() {
        let $cell = $(this);
        let $row = $cell.closest('tr');
        let idx = parseInt($row.data('idx'));
        let header = $cell.data('header');
        let val = $cell.text().trim();
        
        if (previewData[idx] && previewData[idx][header] !== val) {
            previewData[idx][header] = val;
            // Visual feedback for successful edit
            $cell.css('background-color', '#d4edda').animate({backgroundColor: '#fff'}, 1000);
        }
    });
    
    // Handle enter key on editable cells
    $(document).off('keydown', '.editable-cell').on('keydown', '.editable-cell', function(e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            $(this).blur();
        }
    });
    
    
}