document.addEventListener('DOMContentLoaded', () => {
    const initMessageBox = () => {
        const resources = [
            {
                type: 'link',
                href: 'https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css'
            },
            {
                type: 'link',
                href: 'https://fonts.googleapis.com/icon?family=Material+Icons'
            },
            {
                type: 'script',
                src: 'https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js'
            }
        ];

        const loadResource = resource => {
            return new Promise((resolve, reject) => {
                if (resource.type === 'link') {
                    const link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = resource.href;
                    link.onload = resolve;
                    link.onerror = () => reject(resource.href); // Simpan URL yang gagal
                    document.head.appendChild(link);
                } else if (resource.type === 'script') {
                    const script = document.createElement('script');
                    script.src = resource.src;
                    script.onload = resolve;
                    script.onerror = () => reject(resource.src); // Simpan URL yang gagal
                    document.head.appendChild(script);
                }
            });
        };

        Promise.allSettled(resources.map(loadResource))
        .then((results) => {
            // Cek apakah resource kritis (Material Components JS) berhasil di-load
            const jsResult = results[2];
            if (jsResult.status === 'rejected') {
                console.error('Gagal memuat Material Components JS:', jsResult.reason);
                return;
            }

            // Beri peringatan untuk resource lain yang gagal
            results.forEach((result, index) => {
                if (result.status === 'rejected') {
                    console.warn(`Gagal memuat resource: ${resources[index].href || resources[index].src}`, result.reason);
                }
            });

            // Lanjutkan membuat struktur dialog
            const dialog = document.createElement('div');
            dialog.className = 'mdc-dialog';
            dialog.innerHTML = `
            <div class="mdc-dialog__container">
            <div class="mdc-dialog__surface" role="alertdialog">
            <div class="mdc-dialog__header">
            <div class="mdc-dialog__header-icon">
            <i class="material-icons" id="messageIcon"></i>
            </div>
            <h2 class="mdc-dialog__title" id="messageTitle"></h2>
            </div>
            <div class="mdc-dialog__content" id="messageContent"></div>
            <div class="mdc-dialog__actions" id="messageActions"></div>
            </div>
            </div>
            <div class="mdc-dialog__scrim"></div>
            `;
            document.body.appendChild(dialog);

            // Style tambahan
            const style = document.createElement('style');
            style.textContent = `
            .mdc-dialog__header {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                padding: 32px 24px 16px;
            }

            .mdc-dialog__title {
                margin: 16px 0 0 0;
                color: #212121;
                font-size: 20px;
                font-weight: 500;
            }

            .mdc-dialog__header-icon {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 64px;
                height: 64px;
                border-radius: 50%;
                background-color: #f5f5f5;
                font-size: 36px !important;
            }

            .custom-warning .mdc-dialog__header-icon {
                background-color: #fff3e0;
                color: #ffa000;
            }

            .custom-info .mdc-dialog__header-icon {
                background-color: #e3f2fd;
                color: #2196f3;
            }

            .custom-question .mdc-dialog__header-icon {
                background-color: #e8f5e9;
                color: #4caf50;
            }

            .mdc-dialog__actions {
                padding: 8px;
                justify-content: flex-end;
            }
            `;
            document.head.appendChild(style);

            // Pada bagian inisialisasi MDC Dialog
            const messageDialog = new mdc.dialog.MDCDialog(dialog);
            messageDialog.escapeKeyAction = ''; // Nonaktifkan ESC
            messageDialog.scrimClickAction = ''; // Nonaktifkan klik scrim

            const createDialog = (icon, title, message, type, buttons) => {
                return new Promise(resolve => {
                    dialog.classList.remove('custom-warning', 'custom-info', 'custom-question');
                    dialog.classList.add(type);

                    document.getElementById('messageIcon').textContent = icon;
                    document.getElementById('messageTitle').textContent = title;
                    document.getElementById('messageContent').innerHTML = message;

                    const actions = document.getElementById('messageActions');
                    actions.innerHTML = '';

                    let closedHandler = null; // Variabel untuk menyimpan reference handler

                    buttons.forEach(btn => {
                        const button = document.createElement('button');
                        button.className = `mdc-button mdc-button--${btn.type} mdc-dialog__button`;
                        button.innerHTML = `
                        <span class="mdc-button__ripple"></span>
                        <span class="mdc-button__label">${btn.label}</span>
                        `;
                        button.onclick = () => {
                            if (closedHandler) {
                                messageDialog.unlisten('MDCDialog:closed', closedHandler);
                            }
                            messageDialog.close();
                            resolve(btn.value);
                        };
                        actions.appendChild(button);
                    });

                    // Handler untuk penutupan paksa (seharusnya tidak terjadi)
                    closedHandler = (event) => {
                        resolve(null); // Fallback jika ada penutupan tidak terduga
                    };
                    messageDialog.listen('MDCDialog:closed', closedHandler);

                    messageDialog.open();
                });
            };

            window.message_box = {
                alert: (message, title = 'Alert') => {
                    return createDialog(
                        'warning',
                        title,
                        message,
                        'custom-warning',
                        [{ type: 'raised', label: 'OK', value: true }]
                    );
                },

              info: (message, title = 'Information') => {
                  return createDialog(
                      'info',
                      title,
                      message,
                      'custom-info',
                      [{ type: 'raised', label: 'OK', value: true }]
                  );
              },

              yesNo: (message, title = 'Confirmation') => {
                  return createDialog(
                      'help_outline',
                      title,
                      message,
                      'custom-question',
                      [
                          { type: 'outlined', label: 'No', value: false },
                          { type: 'raised', label: 'Yes', value: true }
                      ]
                  );
              }
            };

            document.dispatchEvent(new Event('message_box:ready'));
        })
        .catch(error => {
            console.error('Error loading resources:', error);
        });
    };

    initMessageBox();
});
