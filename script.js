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
            return radio && radio.parentElement && radio.parentElement.textContent ? radio.parentElement.textContent.trim() : value;
        };
        
        // Helper to get display text for select elements
        const getSelectDisplayText = (selectId, value) => {
            if (!value) return 'なし';
            const selectElement = document.getElementById(selectId);
            if (selectElement) {
                const optionElement = selectElement.querySelector(`option[value="${value}"]`);
                if (optionElement) {
                    return optionElement.textContent.trim();
                }
            }
            return value; // Fallback to value if not found
        };

        document.getElementById('summary-department').textContent = getRadioDisplayText('department', data.department);
        document.getElementById('summary-purpose').textContent = getRadioDisplayText('purpose', data.purpose);

        const basicInfoContainer = document.getElementById('summary-basic-info');
        basicInfoContainer.innerHTML = ''; // Clear previous content
        const basicInfoOrder = [
            { key: 'name', label: '名前:' },
            // gender, age, income will be handled with custom formatting
            { key: 'prefecture', label: '都道府県:' },
            { key: 'municipality', label: '市区町村:' },
            { key: 'family', label: '家族構成:' },
            { key: 'occupation', label: '職業:' },
            { key: 'hobby', label: '趣味:' },
            { key: 'life_events', label: 'ライフイベント:' },
        ];

        // --- Custom formatting for specific fields ---
        let genderDisplay = 'なし';
        if (data.gender) {
            genderDisplay = getSelectDisplayText('gender', data.gender);
        }

        let ageDisplay = 'なし';
        if (data.age) {
            ageDisplay = data.age.replace('y', '歳'); 
            if (data.age.includes('m')) { 
                 ageDisplay = data.age.replace('y', '歳').replace('m', 'ヶ月');
            }
        }

        let incomeDisplay = 'なし';
        if (data.income) {
            const incomeValue = data.income;
            if (incomeValue.startsWith('<')) {
                incomeDisplay = `${incomeValue.substring(1)}万円未満`;
            } else if (incomeValue.startsWith('>=')) {
                incomeDisplay = `${incomeValue.substring(2)}万円以上`;
            } else if (incomeValue.includes('-')) {
                incomeDisplay = `${incomeValue}万円`;
            } else {
                incomeDisplay = `${incomeValue}万円`; 
            }
        }
        
        const tempSortedBasicInfo = [];
        const originalOrderKeys = ['name', 'gender', 'age', 'prefecture', 'municipality', 'family', 'occupation', 'income', 'hobby', 'life_events'];
        const valueMap = {
            name: data.name,
            gender: genderDisplay,
            age: ageDisplay,
            prefecture: data.prefecture,
            municipality: data.municipality,
            family: data.family,
            occupation: data.occupation,
            income: incomeDisplay,
            hobby: data.hobby,
            life_events: data.life_events
        };
        const labelMap = {
            name: '名前:',
            gender: '性別:',
            age: '年齢:',
            prefecture: '都道府県:',
            municipality: '市区町村:',
            family: '家族構成:',
            occupation: '職業:',
            income: '年収:',
            hobby: '趣味:',
            life_events: 'ライフイベント:'
        };

        originalOrderKeys.forEach(key => {
            const p = document.createElement('p');
            p.innerHTML = `<strong>${labelMap[key]}</strong> ${valueMap[key] || 'なし'}`;
            basicInfoContainer.appendChild(p);
        });

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
        console.log("Populating results screen with data:", result);
        const profile = result.profile || {}; 

        // Populate New Header Info Section
        let headerDepartmentDisplay = profile.department || '-';
        if (profile.department) {
            const deptRadio = document.querySelector(`input[name="department"][value="${profile.department}"]`);
            if (deptRadio && deptRadio.parentElement && deptRadio.parentElement.textContent) {
                headerDepartmentDisplay = deptRadio.parentElement.textContent.trim();
            }
        }
        document.getElementById('header-department').textContent = headerDepartmentDisplay;

        let headerPurposeDisplay = profile.purpose || '-';
        if (profile.purpose) {
            const purposeRadio = document.querySelector(`input[name="purpose"][value="${profile.purpose}"]`);
            if (purposeRadio && purposeRadio.parentElement && purposeRadio.parentElement.textContent) {
                headerPurposeDisplay = purposeRadio.parentElement.textContent.trim();
            }
        }
        document.getElementById('header-purpose').textContent = headerPurposeDisplay;
        
        // Update image
        document.getElementById('preview-persona-image').src = result.image_url || 'https://via.placeholder.com/150';
        document.getElementById('preview-name').textContent = profile.name || '-';

        // Populate basic info in the preview pane (2-column grid)
        // Department and Purpose are now removed from this specific section in the preview
        // document.getElementById('preview-department').textContent = departmentDisplay; // REMOVED
        // document.getElementById('preview-purpose').textContent = purposeDisplay; // REMOVED

        document.getElementById('preview-gender').textContent = getSelectDisplayTextForResult('gender', profile.gender);
        document.getElementById('preview-age').textContent = formatAgeDisplayForResult(profile.age);
        document.getElementById('preview-prefecture').textContent = profile.prefecture || '-';
        document.getElementById('preview-municipality').textContent = profile.municipality || '-';
        document.getElementById('preview-family').textContent = profile.family || '-';
        document.getElementById('preview-occupation').textContent = profile.occupation || '-';
        document.getElementById('preview-income').textContent = formatIncomeDisplayForResult(profile.income);
        document.getElementById('preview-hobby').textContent = profile.hobby || '-';
        document.getElementById('preview-life_events').textContent = profile.life_events && Array.isArray(profile.life_events) ? profile.life_events.join(', ') : (profile.life_events || '-');
        
        let patientTypeDisplay = profile.patient_type || '-';
        if (profile.patient_type && typeof patientTypeDetails !== 'undefined' && patientTypeDetails[profile.patient_type]) {
            patientTypeDisplay = profile.patient_type; 
        } else if (profile.patient_type) {
            const patientTypeRadio = document.querySelector(`input[name="patient_type"][value="${profile.patient_type}"]`);
            if (patientTypeRadio && patientTypeRadio.parentElement && patientTypeRadio.parentElement.querySelector('.patient-type-name')) {
                patientTypeDisplay = patientTypeRadio.parentElement.querySelector('.patient-type-name').textContent.trim();
            }
        }
        document.getElementById('preview-patient_type').textContent = patientTypeDisplay;

        // Populate Step 4 Fixed Additional Fields (1-column in .additional-info-column)
        document.getElementById('preview-motto').textContent = profile.motto || '-';
        document.getElementById('preview-concerns').textContent = profile.concerns || '-';
        document.getElementById('preview-favorite_person').textContent = profile.favorite_person || '-';
        document.getElementById('preview-media_sns').textContent = profile.media_sns || '-';
        document.getElementById('preview-personality_keywords').textContent = profile.personality_keywords || '-';
        document.getElementById('preview-health_actions').textContent = profile.health_actions || '-';
        document.getElementById('preview-holiday_activities').textContent = profile.holiday_activities || '-';
        document.getElementById('preview-catchphrase_input').textContent = profile.catchphrase || '-'; 

        // Populate Step 4 Dynamically Added Fields (1-column in .additional-info-column)
        const dynamicFieldsContainer = document.getElementById('preview-additional-dynamic-fields');
        dynamicFieldsContainer.innerHTML = ''; 
        if (profile.additional_field_name && profile.additional_field_value &&
            Array.isArray(profile.additional_field_name) && Array.isArray(profile.additional_field_value) &&
            profile.additional_field_name.length === profile.additional_field_value.length) {
            profile.additional_field_name.forEach((fieldName, index) => {
                const fieldValue = profile.additional_field_value[index];
                if (fieldName || fieldValue) { 
                    const p = document.createElement('p');
                    p.innerHTML = `<strong>${fieldName || '項目名なし'}:</strong> ${fieldValue || 'なし'}`;
                    dynamicFieldsContainer.appendChild(p);
                }
            });
        }

        // Populate detailed persona text on the right side
        const detailsContainer = document.querySelector('.persona-details');
        detailsContainer.innerHTML = ''; // Clear previous details

        if (result.generated_text) {
            const detailOrder = [
                { key: 'catchphrase', title: 'キャッチコピー' },
                { key: 'personality_traits', title: '性格・特徴' },
                { key: 'reason_for_visit_and_concerns', title: '来院理由・きっかけ・悩み' },
                { key: 'health_literacy_and_behavior', title: '健康リテラシー・行動変容' },
                { key: 'online_review_evaluation_points', title: '口コミ・評価で重視する点' },
                { key: 'values_and_priorities_in_healthcare', title: '医療における価値観・重視する点' },
                { key: 'requests_to_medical_institution', title: '医療機関に求めるもの' }
            ];
            
            let contentAdded = false;
            detailOrder.forEach(item => {
                if (result.generated_text[item.key]) {
                    const sectionTitle = document.createElement('h4');
                    sectionTitle.textContent = item.title;
                    detailsContainer.appendChild(sectionTitle);

                    const sectionContent = document.createElement('p');
                    if (Array.isArray(result.generated_text[item.key])) {
                         sectionContent.innerHTML = result.generated_text[item.key].map(pText => String(pText || '').replace(/\n/g, '<br>')).join('<br>');
                    } else {
                        sectionContent.innerHTML = String(result.generated_text[item.key] || '').replace(/\n/g, '<br>');
                    }
                    detailsContainer.appendChild(sectionContent);
                    contentAdded = true;
                }
            });

            if (!contentAdded && typeof result.generated_text === 'string') { // Fallback for single string
                const title = document.createElement('h4');
                title.textContent = '生成されたペルソナ詳細';
                detailsContainer.appendChild(title);
                const content = document.createElement('p');
                content.innerHTML = result.generated_text.replace(/\n/g, '<br>');
                detailsContainer.appendChild(content);
            } else if (!contentAdded) {
                 const noResultText = document.createElement('p');
                 noResultText.textContent = 'ペルソナの詳細情報が生成されませんでした。';
                 detailsContainer.appendChild(noResultText);
            }

        } else {
            const noResultText = document.createElement('p');
            noResultText.textContent = 'ペルソナの詳細情報が生成されませんでした。';
            detailsContainer.appendChild(noResultText);
        }

        // 編集可能フィールドのセットアップ
        setupEditableFields();
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

    // 編集可能フィールドの変更イベントを設定する関数
    function setupEditableFields() {
        // 名前フィールドの編集リスナー設定
        const nameField = document.getElementById('preview-name');
        if (nameField) {
            nameField.addEventListener('input', function() {
                // currentPersonaResultを更新
                if (currentPersonaResult && currentPersonaResult.profile) {
                    currentPersonaResult.profile.name = this.textContent;
                }
            });
            
            // フォーカスアウト時のトリミング処理
            nameField.addEventListener('blur', function() {
                this.textContent = this.textContent.trim();
                if (this.textContent === '') {
                    this.textContent = '-';
                }
            });
        }
        
        // 都道府県フィールドの編集リスナー設定
        const prefectureField = document.getElementById('preview-prefecture');
        if (prefectureField) {
            prefectureField.addEventListener('input', function() {
                // currentPersonaResultを更新
                if (currentPersonaResult && currentPersonaResult.profile) {
                    currentPersonaResult.profile.prefecture = this.textContent;
                }
            });
            
            // フォーカスアウト時のトリミング処理
            prefectureField.addEventListener('blur', function() {
                this.textContent = this.textContent.trim();
                if (this.textContent === '') {
                    this.textContent = '-';
                }
            });
        }
        
        // 市区町村フィールドの編集リスナー設定
        const municipalityField = document.getElementById('preview-municipality');
        if (municipalityField) {
            municipalityField.addEventListener('input', function() {
                // currentPersonaResultを更新
                if (currentPersonaResult && currentPersonaResult.profile) {
                    currentPersonaResult.profile.municipality = this.textContent;
                }
            });
            
            // フォーカスアウト時のトリミング処理
            municipalityField.addEventListener('blur', function() {
                this.textContent = this.textContent.trim();
                if (this.textContent === '') {
                    this.textContent = '-';
                }
            });
        }
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

    // Event listener for "最初から" (restart) button
    const restartBtn = document.getElementById('restart-btn');
    if (restartBtn) {
        restartBtn.addEventListener('click', () => {
            // リセット確認
            if (confirm('最初からやり直しますか？入力した内容はすべてリセットされます。')) {
                // フォームをリセット
                document.getElementById('multi-step-form').reset();
                // ステップ1に戻る
                showStep(1);
                // 現在のペルソナ結果をクリア
                currentPersonaResult = null;
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

        // PDFとPPTは常に表示
        if (pdfBtn) pdfBtn.style.display = 'inline-block';
        if (pptBtn) pptBtn.style.display = 'inline-block';

        // Googleスライドは設定に基づいて表示/非表示
        if (gslideBtn) {
            if (settings && settings.output_gslide_enabled) {
                gslideBtn.style.display = 'inline-block';
            } else {
                gslideBtn.style.display = 'none';
            }
        }
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
    showStep(1); // TEMPORARY: Show result screen for UI dev

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

    setupEditableFields();

});

// Helper function (can be moved to a more global scope if needed elsewhere)
function getSelectDisplayTextForResult(selectId, value) {
    if (!value) return '-';
    const selectElement = document.getElementById(selectId);
    if (selectElement) {
        const optionElement = selectElement.querySelector(`option[value="${value}"]`);
        if (optionElement) {
            return optionElement.textContent.trim();
        }
    }
    return value; // Fallback
}

function formatAgeDisplayForResult(ageValue) {
    if (!ageValue) return '-';
    let display = ageValue.replace('y', '歳');
    if (ageValue.includes('m')) {
        display = display.replace('m', 'ヶ月');
    }
    return display;
}

function formatIncomeDisplayForResult(incomeValue) {
    if (!incomeValue) return '-';
    if (incomeValue.startsWith('<')) {
        return `${incomeValue.substring(1)}万円未満`;
    } else if (incomeValue.startsWith('>=')) {
        return `${incomeValue.substring(2)}万円以上`;
    } else if (incomeValue.includes('-')) {
        return `${incomeValue}万円`;
    }
    return `${incomeValue}万円`;
}

/*
// This was inside DOMContentLoaded, needs to be global or passed for populateResults to use it.
// Consider moving this to a global scope or a shared utility object/module.
const patientTypeDetails = {
    '利便性重視型': { description: '...', example: '...' },
    // ... other types
};
*/ 