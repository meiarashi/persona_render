document.addEventListener('DOMContentLoaded', async () => {
    let currentPersonaResult = null;

    const multiStepForm = document.getElementById('multi-step-form');
    const formSteps = multiStepForm.querySelectorAll('.form-step');
    const nextButtons = multiStepForm.querySelectorAll('.next-step-btn');
    const prevButtons = multiStepForm.querySelectorAll('.prev-step-btn');
    const departmentRadios = multiStepForm.querySelectorAll('input[name="department"]');
    const purposeRadios = multiStepForm.querySelectorAll('input[name="purpose"]');
    const settingTypeRadios = multiStepForm.querySelectorAll('input[name="setting_type"]');
    const detailedSettingsDiv = document.getElementById('detailed-settings');
    const autoSettingInfo = document.getElementById('auto-setting-info');
    const addFieldButton = document.getElementById('add-field-btn');
    const additionalFieldsContainer = document.getElementById('additional-fields');
    const confirmAndProceedBtns = document.querySelectorAll('.confirm-and-proceed-btn');
    const editBackButton = multiStepForm.querySelector('.result-step .prev-step-btn'); // Result step back button
    const mainContainer = document.querySelector('.main-container');
    const patientTypeSelectionDiv = document.getElementById('patient-type-selection'); // New patient type container
    const patientTypeDescriptionDiv = document.getElementById('patient-type-description'); // New description area
    const patientTypeRadios = multiStepForm.querySelectorAll('input[name="patient_type"]'); // New patient type radios

    // New elements for confirmation screen
    const finalGenerateBtns = document.querySelectorAll('.final-generate-btn-common');
    const editStepButtons = multiStepForm.querySelectorAll('.edit-step-btn');

    let currentStep = 1;
    const TOTAL_FORM_STEPS = 5; // Step 1-4 for input, Step 5 for confirmation
    let hasVisitedConfirmationScreen = false; // 「確認画面を見たか」のフラグ

    // --- Patient Type Descriptions (Store features and examples) ---
    const patientTypeDetails = {
        '利便性重視型': { description: 'アクセスの良さ、待ち時間の短さ、診療時間の柔軟性など、便利さを最優先', example: '忙しいビジネスパーソン、オンライン診療を好む患者' },
        '専門医療追求型': { description: '専門医や高度専門医療機関での治療を希望し、医師の経歴や実績を重視', example: '難病患者、複雑な症状を持つ患者' },
        '予防健康管理型': { description: '病気になる前の予防や早期発見、健康維持に関心が高い', example: '定期健診を欠かさない人、予防接種に積極的な人' },
        '代替医療志向型': { description: '漢方、鍼灸、ホメオパシーなど、西洋医学以外の選択肢を積極的に取り入れる', example: '自然療法愛好者、慢性疾患の患者' },
        '経済合理型': { description: '自己負担額、保険適用の有無、費用対効果を重視', example: '経済的制約のある患者、医療費控除を意識する人' },
        '情報探求型': { description: '徹底的な情報収集、セカンドオピニオン取得、比較検討を行う', example: '高学歴層、慎重な意思決定を好む患者' },
        '革新技術指向型': { description: '最先端の医療技術、新薬、臨床試験などに積極的に関心を持つ', example: '既存治療で効果が出なかった患者、医療イノベーションに関心がある人' },
        '対話重視型': { description: '医師からの丁寧な説明や対話を求め、質問が多い', example: '不安を感じやすい患者、医療従事者' },
        '信頼基盤型': { description: 'かかりつけ医との長期的な関係や医療機関の評判を重視', example: '地域密着型の患者、同じ医師に長期通院する患者' },
        '緊急解決型': { description: '症状の即時改善を求め、緊急性を重視', example: '急性疾患患者、痛みに耐性が低い患者' },
        '受動依存型': { description: '医師の判断に全面的に依存し、自らの決定より医師の指示を優先', example: '高齢者、医療知識が少ない患者' },
        '自律決定型': { description: '自分の治療に主体的に関わり、最終決定権を持ちたいと考える', example: '医療リテラシーが高い患者、自己管理を好む慢性疾患患者' }
    };

    // Add querySelectorAll for purpose labels and radios here
    const purposeLabels = multiStepForm.querySelectorAll('.purpose-options label');

    window.currentOutputSettings = { pdf: true, ppt: true, gslide: false }; // Initialize with defaults

    try {
        const response = await fetch('/api/settings/output'); 
        if (response.ok) {
            const outputSettings = await response.json();
            console.log("Fetched output settings for user:", outputSettings);
            window.currentOutputSettings = outputSettings; 
            // DO NOT call updateDownloadButtonVisibility here, buttons may not exist.
        } else {
            console.error("Failed to fetch output settings for user:", response.status);
            // Keep default settings if fetch fails
        }
    } catch (error) {
        console.error("Error fetching output settings:", error);
        // Keep default settings on error
    }

    // --- Helper Functions ---
    function showStep(stepNumber) {
        // Hide all steps first
        formSteps.forEach(step => {
            step.classList.remove('active');
        });

        // まず全ての initially-hidden-confirm-btn を非表示にする (他のステップに移動した際に隠すため)
        document.querySelectorAll('.initially-hidden-confirm-btn').forEach(btn => {
            btn.classList.remove('force-show-confirm-btn'); // 表示用クラスを削除
            if (!btn.classList.contains('initially-hidden-confirm-btn')) { // もしinitially-hiddenがないなら（Step4のボタンなど）何もしない
                // ここは現状維持
            }
        });

        // Show the target step
        const nextStepElement = multiStepForm.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (nextStepElement) {
            nextStepElement.classList.add('active');
            currentStep = stepNumber;
            
            // Update progress bar text and fill based on the current active step
            const progressBarSpan = nextStepElement.querySelector('.progress-bar span');
            const progressBarFill = nextStepElement.querySelector('.progress-bar .progress');

            if (progressBarSpan && progressBarFill) {
                if (stepNumber <= 4) { // Steps 1-4 for input
                    progressBarSpan.textContent = `${stepNumber}/${TOTAL_FORM_STEPS -1}問目`; // Total input questions = 4
                    progressBarFill.style.width = `${(stepNumber / (TOTAL_FORM_STEPS -1)) * 100}%`;
                } else if (stepNumber === TOTAL_FORM_STEPS) { // Step 5 is confirmation
                    progressBarSpan.textContent = '入力内容の確認';
                    progressBarFill.style.width = '100%';
                }
                // For loading (step 6) and result (step 7), progress bar might not be relevant or is handled differently
            }

            if (stepNumber === 7) { // Result step is now 7
                mainContainer.classList.add('result-active');
                if (window.currentOutputSettings) {
                    updateDownloadButtonVisibility(window.currentOutputSettings);
                } else {
                    console.warn("window.currentOutputSettings not set when trying to show step 7 buttons");
                    updateDownloadButtonVisibility({ pdf: true, ppt: true, gslide: false }); 
                }
            } else {
                mainContainer.classList.remove('result-active');
            }

            // 「入力内容の確認へ進む」ボタンの表示制御 (Steps 1, 2, 3 のみ対象)
            if (hasVisitedConfirmationScreen && (stepNumber === 1 || stepNumber === 2 || stepNumber === 3)) {
                const confirmBtnInStep = nextStepElement.querySelector('.initially-hidden-confirm-btn');
                if (confirmBtnInStep) {
                    confirmBtnInStep.classList.add('force-show-confirm-btn'); // 表示用クラスを追加
                }
            }
        }
    }

    function getFormData() {
        const formData = new FormData(multiStepForm);
        const data = {};

        formData.forEach((value, key) => {
            if (key.endsWith('[]')) {
                 const cleanKey = key.slice(0, -2);
                 if (!data[cleanKey]) {
                     data[cleanKey] = [];
                 }
                 data[cleanKey].push(value);
            } else if (key !== 'setting_type') { 
                 data[key] = value;
            }
        });

        // setting_type の値をチェックされているラジオボタンから直接取得して設定
        const checkedSettingTypeRadio = document.querySelector('input[name="setting_type"]:checked');
        if (checkedSettingTypeRadio) {
            data['setting_type'] = checkedSettingTypeRadio.value;
        } else {
            data['setting_type'] = 'detailed'; // Fallback
        }

        // Selected department (no longer depends on tabs)
        const departmentRadio = multiStepForm.querySelector('input[name="department"]:checked');
        if(departmentRadio) {
            data['department'] = departmentRadio.value;
        }
         // Patient type is already collected by formData.forEach if a radio is checked.
        // If no patient_type is checked and setting_type is 'patient_type',
        // it might be undefined in data. This is handled in populateConfirmationScreen.

        console.log("Collected Form Data:", data);
        return data;
    }

    function populateConfirmationScreen(data) {
        console.log("Populating confirmation screen with data:", data);

        // Helper to get display text for radio button values
        const getRadioDisplayText = (groupName, value) => {
            if (!value) return 'なし';
            const radio = document.querySelector(`input[name="${groupName}"][value="${value}"]`);
            // Make sure to access textContent of the label, not the radio itself
            return radio && radio.parentElement && radio.parentElement.textContent ? radio.parentElement.textContent.trim() : value;
        };

        document.getElementById('summary-department').textContent = getRadioDisplayText('department', data.department);
        document.getElementById('summary-purpose').textContent = getRadioDisplayText('purpose', data.purpose);

        const basicInfoContainer = document.getElementById('summary-basic-info');
        basicInfoContainer.innerHTML = ''; // Clear previous content
        const basicInfoOrder = [
            { key: 'name', label: '名前:' },
            { key: 'gender', label: '性別:' },
            { key: 'age', label: '年齢:' },
            { key: 'prefecture', label: '都道府県:' },
            { key: 'municipality', label: '市区町村:' },
            { key: 'family', label: '家族構成:' },
            { key: 'occupation', label: '職業:' },
            { key: 'income', label: '年収:' },
            { key: 'hobby', label: '趣味:' },
            { key: 'life_events', label: 'ライフイベント:' },
            // patient_type is handled separately if setting_type was 'patient_type'
        ];

        basicInfoOrder.forEach(item => {
            let value = data[item.key];
            // For gender, get the display text if a value exists
            if (item.key === 'gender' && value) {
                value = getRadioDisplayText('gender', value);
            }
            const p = document.createElement('p');
            p.innerHTML = `<strong>${item.label}</strong> ${value || 'なし'}`;
            basicInfoContainer.appendChild(p);
        });

        // 患者タイプが存在する場合、基本情報セクションの最後に追加表示
        if (data.patient_type) {
            const p = document.createElement('p');
            p.innerHTML = `<strong>患者タイプ:</strong> ${getRadioDisplayText('patient_type', data.patient_type) || 'なし'}`;
            basicInfoContainer.appendChild(p);
        }

        const additionalFixedContainer = document.getElementById('summary-additional-fixed-info');
        additionalFixedContainer.innerHTML = ''; // まず固定項目表示エリアをクリア
        const fixedFieldsOrder = [
            { key: 'motto', label: '座右の銘:' },
            { key: 'concerns', label: '最近の悩み/関心:' },
            { key: 'favorite_person', label: '好きな有名人/尊敬する人物:' },
            { key: 'media_sns', label: 'よく見るメディア/SNS:' },
            { key: 'personality_keywords', label: '性格キーワード（3語以内）:' },
            { key: 'health_actions', label: '最近した健康に関する行動:' },
            { key: 'holiday_activities', label: '休日の過ごし方:' },
            { key: 'catchphrase', label: 'キャッチコピー:' }
        ];

        fixedFieldsOrder.forEach(item => {
            const value = data[item.key];
            const p = document.createElement('p');
            p.innerHTML = `<strong>${item.label}</strong> ${value || 'なし'}`;
            additionalFixedContainer.appendChild(p);
        });

        if (data.additional_field_name && data.additional_field_value && data.additional_field_name.length === data.additional_field_value.length) {
            // Check if there is at least one non-empty field name or field value
            const hasDynamicData = data.additional_field_name.some((name, i) => name || data.additional_field_value[i]);

            if (hasDynamicData) {
                data.additional_field_name.forEach((fieldName, index) => {
                    const fieldValue = data.additional_field_value[index];
                    // Display if either fieldName or fieldValue has content
                    if (fieldName || fieldValue) { 
                        const p = document.createElement('p');
                        p.innerHTML = `<strong>${fieldName || '項目名なし'}:</strong> ${fieldValue || 'なし'}`;
                        additionalFixedContainer.appendChild(p); // Add to fixed container
                    }
                });
            }
        }
        hasVisitedConfirmationScreen = true; // 確認画面が表示されたのでフラグを立てる
    }

    // --- Event Listeners ---

    // Department Radios (Step 1)
    departmentRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            updateSelectedLabel(departmentRadios, 'department');
        });
    });

    // Purpose Radios (Step 2) - Use the helper function
    purposeRadios.forEach(radio => {
        radio.addEventListener('change', (event) => {
            updateSelectedLabel(purposeRadios, 'purpose');
        });
    });

    // Setting Type Radios (Step 3) - Use the helper function and handle display logic
    settingTypeRadios.forEach(radio => {
        radio.addEventListener('change', (event) => {
            updateSelectedLabel(settingTypeRadios, 'setting_type'); // Update button selection style
            // Show/hide different setting sections based on selection
            const settingType = event.target.value;
            
            if (settingType === 'input') {
                detailedSettingsDiv.style.display = 'block';
                autoSettingInfo.style.display = 'none';
                patientTypeSelectionDiv.style.display = 'none'; // Hide patient type grid
            } else if (settingType === 'auto') {
                detailedSettingsDiv.style.display = 'none';
                autoSettingInfo.style.display = 'block';
                patientTypeSelectionDiv.style.display = 'none'; // Hide patient type grid
            } else if (settingType === 'patient_type') {
                detailedSettingsDiv.style.display = 'none';
                autoSettingInfo.style.display = 'none';
                patientTypeSelectionDiv.style.display = 'flex'; // Use flex to allow centering via CSS
                
                // 初期表示時も「利便性重視型」を自動選択
                const convenientTypeRadio = document.getElementById('pt-convenience');
                if (convenientTypeRadio) {
                    convenientTypeRadio.checked = true;
                    
                    // 選択済みスタイルを適用
                    multiStepForm.querySelectorAll('.patient-type-item').forEach(item => {
                        item.classList.remove('selected');
                    });
                    const parentItem = convenientTypeRadio.closest('.patient-type-item');
                    if (parentItem) {
                        parentItem.classList.add('selected');
                    }
                    
                    // 説明を表示
                    const details = patientTypeDetails['利便性重視型'];
                    if (details) {
                        patientTypeDescriptionDiv.innerHTML = `
                            <h5>利便性重視型</h5>
                            <p><strong>特徴:</strong> ${details.description}</p>
                            <p><strong>例:</strong> ${details.example}</p>
                        `;
                        patientTypeDescriptionDiv.style.display = 'block';
                    }
                }
            } else { // Default / Fallback
                 detailedSettingsDiv.style.display = 'block';
                 autoSettingInfo.style.display = 'none';
                 patientTypeSelectionDiv.style.display = 'none';
            }
        });
    });

    // Add click listener to the grid container for patient type selection
    const patientTypeGrid = document.querySelector('.patient-type-grid');
    if (patientTypeGrid) {
        patientTypeGrid.addEventListener('click', (event) => {
            const targetItem = event.target.closest('.patient-type-item');
            if (!targetItem) return; // Clicked outside an item

            // Find the radio button within the clicked item and check it
            const radio = targetItem.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;

                // Update visual selection
                multiStepForm.querySelectorAll('.patient-type-item').forEach(item => {
                    item.classList.remove('selected');
                });
                targetItem.classList.add('selected');

                // Show description
                const selectedValue = radio.value;
                const details = patientTypeDetails[selectedValue];
                if (details) {
                    patientTypeDescriptionDiv.innerHTML = `
                        <h5>${selectedValue}</h5>
                        <p><strong>特徴:</strong> ${details.description}</p>
                        <p><strong>例:</strong> ${details.example}</p>
                    `;
                    patientTypeDescriptionDiv.style.display = 'block';
                } else {
                    patientTypeDescriptionDiv.innerHTML = '';
                    patientTypeDescriptionDiv.style.display = 'none';
                }
            } else {
                console.warn('Could not find radio button within the clicked patient type item.');
            }
        });
    }

    // Next Step Buttons
    nextButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (currentStep === 1) {
                const selectedDept = multiStepForm.querySelector('input[name="department"]:checked');
                if (!selectedDept) {
                    alert('診療科を選択してください。');
                    return;
                }
            }
             // Add validation for other steps if needed
             if (currentStep < TOTAL_FORM_STEPS -1) { // Go to next input step (1 to 4)
                showStep(currentStep + 1);
             }
        });
    });

    // Previous Step Buttons
    prevButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Check if the button is inside the confirmation step (step 5)
            const parentStep = button.closest('.form-step');
            if (parentStep && parentStep.dataset.step === "5") {
                showStep(4); // Go back to additional info (step 4)
            } else if (currentStep > 1) {
                showStep(currentStep - 1);
            }
        });
    });

    // Edit Back Button (from Result Step 7 to Confirmation Step 5)
    if (editBackButton) {
        editBackButton.addEventListener('click', () => {
            showStep(TOTAL_FORM_STEPS); // Show confirmation screen (Step 5)
        });
    }

    // New: Event listener for all "Confirm and Proceed" buttons (Steps 1-4)
    confirmAndProceedBtns.forEach(button => {
        button.addEventListener('click', async () => {
            const formData = getFormData();
            populateConfirmationScreen(formData);
            showStep(TOTAL_FORM_STEPS); // Show confirmation screen (Step 5)
        });
    });

    // Edit Step Buttons (On Confirmation Screen)
    editStepButtons.forEach(button => {
        button.addEventListener('click', () => {
            hasVisitedConfirmationScreen = true; // 編集ボタンで戻る際もフラグを立てる
            const targetStep = parseInt(button.dataset.step);
            if (targetStep > 0 && targetStep < TOTAL_FORM_STEPS) {
                showStep(targetStep);
                // If returning to step 3, restore setting_type view
                if (targetStep === 3) {
                    const formData = getFormData(); // Get current form data to know the setting_type
                    const settingType = formData.setting_type || 'input'; // default to 'input' if not found
                    const radioToSelect = document.querySelector(`input[name="setting_type"][value="${settingType}"]`);
                    if (radioToSelect) {
                        radioToSelect.checked = true;
                        // Manually trigger change event to update UI sections
                        radioToSelect.dispatchEvent(new Event('change'));
                    }
                }
            }
        });
    });

    // Event listener for the final persona generation button
    finalGenerateBtns.forEach(button => {
        button.addEventListener('click', async function() {
            // Show loading screen
            formSteps.forEach(step => step.classList.remove('active'));
            const loadingStep = document.querySelector('.loading-step');
            loadingStep.classList.add('active');
            
            const data = getFormData();
            currentPersonaResult = null; // Reset previous result

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'ペルソナ生成中に不明なエラーが発生しました。' }));
                    throw new Error(errorData.detail || `サーバーエラー: ${response.status}`);
                }

                const result = await response.json();
                currentPersonaResult = result; // Store the result
                
                // Call showStep before populateResults
                showStep(TOTAL_FORM_STEPS + 2); // Show result screen (Step 7)
                // Delay populateResults to allow DOM to update
                setTimeout(() => {
                    populateResults(result); // Populate results on Step 7
                }, 0); 

            } catch (error) {
                console.error('Error generating persona:', error);
                alert(`ペルソナ生成に失敗しました: ${error.message}`);
                showStep(TOTAL_FORM_STEPS); // Go back to confirmation screen on error
            } finally {
                // Hide loading screen
                loadingStep.classList.remove('active');
            }
        });
    });

    // Add Additional Field Button (Step 4)
    addFieldButton.addEventListener('click', () => {
        const newFieldRow = document.createElement('div');
        newFieldRow.classList.add('additional-field-row');
        newFieldRow.innerHTML = `
            <input type="text" name="additional_field_name[]" placeholder="項目">
            <input type="text" name="additional_field_value[]" placeholder="内容">
            <button type="button" class="remove-field-btn" style="background-color: #dc3545; color: white; padding: 5px 10px; border: none; border-radius: 4px; cursor: pointer; height: fit-content; align-self: center;">削除</button>
        `;
        additionalFieldsContainer.appendChild(newFieldRow);
    });

    // Remove Additional Field Button (Event Delegation)
    additionalFieldsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('remove-field-btn')) {
            event.target.closest('.additional-field-row').remove();
        }
    });

    function populateResults(result) {
        // Populate right side (persona details)
        document.getElementById('result-personality').textContent = result.details?.personality || '-';
        document.getElementById('result-reason').textContent = result.details?.reason || '-';
        document.getElementById('result-behavior').textContent = result.details?.behavior || '-';
        document.getElementById('result-reviews').textContent = result.details?.reviews || '-';
        document.getElementById('result-values').textContent = result.details?.values || '-';
        document.getElementById('result-demands').textContent = result.details?.demands || '-';
        // Add more fields if the backend provides them

        // Populate left side (preview profile)
        document.getElementById('preview-persona-image').src = result.image_url || ''; // Changed to result.image_url
        document.getElementById('preview-name').textContent = result.profile?.name || '-';
        // Display prefecture and municipality if available
        let locationText = '-';
        if (result.profile?.prefecture && result.profile?.municipality) {
            locationText = `${result.profile.prefecture} ${result.profile.municipality}`;
        } else if (result.profile?.prefecture) {
            locationText = result.profile.prefecture;
        } else if (result.profile?.municipality) {
            locationText = result.profile.municipality;
        } else if (result.profile?.location) { // Fallback to old location if new fields not present
            locationText = result.profile.location;
        }
        document.getElementById('preview-location').textContent = locationText;

        // Separate Gender and Age population
        document.getElementById('preview-gender').textContent = result.profile?.gender || '-';
        document.getElementById('preview-age').textContent = result.profile?.age || '-'; 
        // Remove combined population: document.getElementById('preview-gender-age').textContent = `${result.profile?.gender || '-'} | ${result.profile?.age || '-'}`;
        document.getElementById('preview-occupation').textContent = result.profile?.occupation || '-';
        document.getElementById('preview-income').textContent = result.profile?.income || '-';
        document.getElementById('preview-hobby').textContent = result.profile?.hobby || '-';
        // Add handling for additional fields if displayed in preview
    }

    // --- Download Functionality ---

    // Helper function to trigger browser download
    function triggerDownload(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    }

    // Event listener for PDF download button
    const pdfDownloadBtn = document.getElementById('download-pdf-result');
    if (pdfDownloadBtn) {
        pdfDownloadBtn.addEventListener('click', async () => {
            if (!currentPersonaResult) {
                alert('ペルソナがまだ生成されていません。');
                return;
            }
            if (!currentPersonaResult.profile || !currentPersonaResult.details) {
                 alert('ペルソナデータが不完全です。');
                 console.error("Incomplete persona data for download:", currentPersonaResult);
                 return;
            }

            // Add a simple loading indicator (optional)
            const originalText = pdfDownloadBtn.textContent;
            pdfDownloadBtn.textContent = '生成中...';
            pdfDownloadBtn.disabled = true;

            try {
                const response = await fetch('/api/download/pdf', { // Changed to relative path
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(currentPersonaResult), // Send the stored result
                });

                if (!response.ok) {
                    // Try to parse error message from backend
                    let errorMsg = 'PDFの生成に失敗しました。';
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.error || errorMsg;
                    } catch (e) {
                        // Ignore if response is not JSON
                    }
                    throw new Error(errorMsg + ` (Status: ${response.status})`);
                }

                const blob = await response.blob();
                // Extract filename from Content-Disposition header if available, otherwise generate one
                const contentDisposition = response.headers.get('content-disposition');
                let filename = `${currentPersonaResult.profile.name || 'persona'}_persona.pdf`; // Default filename
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                    if (filenameMatch && filenameMatch.length > 1) {
                        filename = filenameMatch[1];
                    }
                }
                triggerDownload(blob, filename);

            } catch (error) {
                console.error('PDF Download Error:', error);
                alert(`エラーが発生しました: ${error.message}`);
            } finally {
                 // Restore button text and state
                pdfDownloadBtn.textContent = originalText;
                pdfDownloadBtn.disabled = false;
            }
        });
    }

    // Placeholder for PPT download button
    const pptDownloadBtn = document.getElementById('download-ppt-result');
    if (pptDownloadBtn) {
        pptDownloadBtn.addEventListener('click', async () => {
            if (!currentPersonaResult) {
                alert('ペルソナがまだ生成されていません。');
                return;
            }
            if (!currentPersonaResult.profile || !currentPersonaResult.details) {
                 alert('ペルソナデータが不完全です。');
                 console.error("Incomplete persona data for download:", currentPersonaResult);
                 return;
            }

            // Add loading indicator
            const originalText = pptDownloadBtn.textContent;
            pptDownloadBtn.textContent = '生成中...';
            pptDownloadBtn.disabled = true;

            try {
                const response = await fetch('/api/download/ppt', { // Changed to relative path
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(currentPersonaResult),
                });

                if (!response.ok) {
                    let errorMsg = 'PPTの生成に失敗しました。';
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.error || errorMsg;
                    } catch (e) { /* Ignore */ }
                    throw new Error(errorMsg + ` (Status: ${response.status})`);
                }

                const blob = await response.blob();
                const contentDisposition = response.headers.get('content-disposition');
                let filename = `${currentPersonaResult.profile.name || 'persona'}_persona.pptx`; // Default .pptx
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                    if (filenameMatch && filenameMatch.length > 1) {
                        filename = filenameMatch[1];
                    }
                }
                triggerDownload(blob, filename);

            } catch (error) {
                console.error('PPT Download Error:', error);
                alert(`エラーが発生しました: ${error.message}`);
            } finally {
                // Restore button
                pptDownloadBtn.textContent = originalText;
                pptDownloadBtn.disabled = false;
            }
        });
    }

    // Placeholder for Google Slides download button
    const gslideDownloadBtn = document.getElementById('download-gslide-result');
    if (gslideDownloadBtn) {
         gslideDownloadBtn.addEventListener('click', () => {
            alert('Google スライド エクスポート機能は現在開発中です。');
        });
    }

    // --- Function to control button visibility ---
    function updateDownloadButtonVisibility(settings) {
        console.log("Updating download button visibility with settings:", settings);
        const pdfBtn = document.getElementById('download-pdf-result');
        const pptBtn = document.getElementById('download-ppt-result');
        const gslideBtn = document.getElementById('download-gslide-result');

        if (!settings) {
            console.warn("Output settings are undefined, cannot update button visibility.");
            if (pdfBtn) pdfBtn.style.display = 'none';
            if (pptBtn) pptBtn.style.display = 'none';
            if (gslideBtn) gslideBtn.style.display = 'none';
            return;
        }

        // バックエンドAPIが返すキー名に合わせて修正
        if (pdfBtn) pdfBtn.style.display = settings.output_pdf_enabled ? 'inline-block' : 'none';
        if (pptBtn) pptBtn.style.display = settings.output_ppt_enabled ? 'inline-block' : 'none';
        if (gslideBtn) gslideBtn.style.display = settings.output_gslide_enabled ? 'inline-block' : 'none';
    }

    // Function to update the .selected class on labels
    function updateSelectedLabel(radios, type) {
        // Remove selected class from all labels
        let optionsContainer;
        if (type === 'setting_type') {
            // Use direct class selector specifically for setting_type
            optionsContainer = multiStepForm.querySelector('.setting-type-options');
        } else {
            // Use attribute selector for others (like purpose, department)
            optionsContainer = multiStepForm.querySelector(`div[class*="${type}-options"]`);
        }

        if (optionsContainer) {
            const labels = optionsContainer.querySelectorAll('label');
            labels.forEach(label => {
                label.classList.remove('selected');
            });
        } 
        
        // Add selected class to the label of the checked radio
        const checkedRadio = multiStepForm.querySelector(`input[name="${type}"]:checked`);
        if (checkedRadio) {
            const parentLabel = checkedRadio.closest('label');
            if (parentLabel) {
                parentLabel.classList.add('selected');
            }
        }
    }

    // --- Initial Setup --- 
    showStep(1); // Show the first step initially

    // Set initial selected class based on checked radios (replaces initial updateSelectedLabel calls)
    ['department', 'purpose', 'setting_type'].forEach(type => {
        const checkedRadio = multiStepForm.querySelector(`input[name="${type}"]:checked`);
        if (checkedRadio) {
            const parentLabel = checkedRadio.closest('label');
            if (parentLabel) {
                // Find all labels for this type and remove selected first
                const container = parentLabel.closest(`div[class*="${type.replace('_', '-')}-options"]`);
                if(container){
                    container.querySelectorAll('label').forEach(lbl => lbl.classList.remove('selected'));
                }
                // Then add selected class to the correct one
                parentLabel.classList.add('selected');
            }
        }
    });

    // Initialize state for step 3 display (after setting initial class)
    const initialSettingTypeRadio = document.querySelector('input[name="setting_type"]:checked');
    if (initialSettingTypeRadio) {
        const initialSettingType = initialSettingTypeRadio.value;
        if (initialSettingType === 'input') {
            detailedSettingsDiv.style.display = 'block';
            autoSettingInfo.style.display = 'none';
            patientTypeSelectionDiv.style.display = 'none';
        } else if (initialSettingType === 'auto') {
            detailedSettingsDiv.style.display = 'none';
            autoSettingInfo.style.display = 'block';
            patientTypeSelectionDiv.style.display = 'none';
        } else if (initialSettingType === 'patient_type') {
             detailedSettingsDiv.style.display = 'none';
             autoSettingInfo.style.display = 'none';
             patientTypeSelectionDiv.style.display = 'flex';
             
             // 初期表示時も「利便性重視型」を自動選択
             const convenientTypeRadio = document.getElementById('pt-convenience');
             if (convenientTypeRadio) {
                 convenientTypeRadio.checked = true;
                 
                 // 選択済みスタイルを適用
                 multiStepForm.querySelectorAll('.patient-type-item').forEach(item => {
                     item.classList.remove('selected');
                 });
                 const parentItem = convenientTypeRadio.closest('.patient-type-item');
                 if (parentItem) {
                     parentItem.classList.add('selected');
                 }
                 
                 // 説明を表示
                 const details = patientTypeDetails['利便性重視型'];
                 if (details) {
                     patientTypeDescriptionDiv.innerHTML = `
                         <h5>利便性重視型</h5>
                         <p><strong>特徴:</strong> ${details.description}</p>
                         <p><strong>例:</strong> ${details.example}</p>
                     `;
                     patientTypeDescriptionDiv.style.display = 'block';
                 }
             }
        } else { // Default
             detailedSettingsDiv.style.display = 'block';
             autoSettingInfo.style.display = 'none';
             patientTypeSelectionDiv.style.display = 'none';
        }
    } else { 
        // Default case if nothing is checked initially for setting_type
         if (detailedSettingsDiv) detailedSettingsDiv.style.display = 'block'; // Default to input view
         if (autoSettingInfo) autoSettingInfo.style.display = 'none';
         if (patientTypeSelectionDiv) patientTypeSelectionDiv.style.display = 'none';
    }

}); 