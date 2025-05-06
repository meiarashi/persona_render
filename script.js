document.addEventListener('DOMContentLoaded', async () => {
    let currentPersonaResult = null;

    const multiStepForm = document.getElementById('multi-step-form');
    const formSteps = multiStepForm.querySelectorAll('.form-step');
    const nextButtons = multiStepForm.querySelectorAll('.next-step-btn');
    const prevButtons = multiStepForm.querySelectorAll('.prev-step-btn');
    const tabButtons = multiStepForm.querySelectorAll('.tab-button');
    const departmentDoctorRadios = multiStepForm.querySelectorAll('input[name="department_doctor"]');
    const departmentDentistRadios = multiStepForm.querySelectorAll('input[name="department_dentist"]');
    const purposeRadios = multiStepForm.querySelectorAll('input[name="purpose"]');
    const purposeOtherDetails = document.getElementById('purpose-other-details');
    const settingTypeRadios = multiStepForm.querySelectorAll('input[name="setting_type"]');
    const detailedSettingsDiv = document.getElementById('detailed-settings');
    const autoSettingInfo = document.getElementById('auto-setting-info');
    const addFieldButton = document.getElementById('add-field-btn');
    const additionalFieldsContainer = document.getElementById('additional-fields');
    const generatePersonaButton = document.getElementById('generate-persona-btn');
    const editBackButton = multiStepForm.querySelector('.result-step .prev-step-btn'); // Result step back button
    const resultProfileContainer = document.getElementById('result-profile-container'); // Left preview profile info
    const imagePreviewPlaceholder = document.querySelector('.image-placeholder'); // Original placeholder
    const previewDescription = document.querySelector('.preview-area .description'); // Original description
    const previewArea = document.querySelector('.preview-area');
    const mainContainer = document.querySelector('.main-container');

    let currentStep = 1;
    let currentTab = 'doctor'; // Default tab

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

        // Show the target step
        const nextStepElement = multiStepForm.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (nextStepElement) {
            nextStepElement.classList.add('active');
            currentStep = stepNumber;
            
            const mainContainer = document.querySelector('.main-container');
            
            if (stepNumber === 6) { // Result step
                resultProfileContainer.style.display = 'block';
                imagePreviewPlaceholder.style.display = 'none';
                previewDescription.style.display = 'none';
                mainContainer.classList.add('result-active');
                // Call updateDownloadButtonVisibility here, now that step 6 is active
                if (window.currentOutputSettings) {
                    updateDownloadButtonVisibility(window.currentOutputSettings);
                } else {
                    console.warn("window.currentOutputSettings not set when trying to show step 6 buttons");
                    // Fallback to default or hide all if really not set
                    updateDownloadButtonVisibility({ pdf: true, ppt: true, gslide: false }); 
                }
            } else {
                resultProfileContainer.style.display = 'none';
                imagePreviewPlaceholder.style.display = 'block';
                previewDescription.style.display = 'block';
                mainContainer.classList.remove('result-active');
            }
        }
    }

    function getFormData() {
        const formData = new FormData(multiStepForm);
        const data = {};
        // Collect data from all steps
        formData.forEach((value, key) => {
            // Handle multiple values for the same key (like additional fields)
            if (key.endsWith('[]')) {
                 const cleanKey = key.slice(0, -2);
                 if (!data[cleanKey]) {
                     data[cleanKey] = [];
                 }
                 data[cleanKey].push(value);
            } else {
                 data[key] = value;
            }
        });

        // Add selected department based on active tab
        const activeTab = multiStepForm.querySelector('.tab-content.active');
        if (activeTab) {
            const departmentRadio = activeTab.querySelector('input[name^="department_"]:checked');
            if(departmentRadio) {
                data['department'] = departmentRadio.value;
                 // Remove the specific doctor/dentist keys if needed
                 delete data['department_doctor'];
                 delete data['department_dentist'];
            }
        }

        console.log("Collected Form Data:", data);
        return data;
    }

    function updateTabs(targetTabId) {
        tabButtons.forEach(button => {
            button.classList.remove('active');
            if (button.dataset.target === targetTabId) {
                button.classList.add('active');
            }
        });
        multiStepForm.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
            if (content.id === `${targetTabId}-content`) {
                content.classList.add('active');
            }
        });
        currentTab = targetTabId;
    }

    // --- Event Listeners ---

    // Next Step Buttons
    nextButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Basic validation (example for step 1)
            if (currentStep === 1) {
                const selectedDept = multiStepForm.querySelector(`input[name="department_${currentTab}"]:checked`);
                if (!selectedDept) {
                    alert('診療科を選択してください。');
                    return;
                }
            }
             // Add validation for other steps if needed
             if (currentStep < 6) { // Ensure we don't go beyond step 4 manually
                showStep(currentStep + 1);
             }
        });
    });

    // Previous Step Buttons
    prevButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (currentStep > 1) {
                // Special case for returning from result (step 6)
                if (currentStep === 6) {
                    showStep(4); // Go back to additional questions
                } else {
                    showStep(currentStep - 1);
                }
            }
        });
    });

    // Tab Buttons (Step 1)
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            updateTabs(button.dataset.target);
        });
    });

    // Purpose Radios (Step 2)
    purposeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            if (radio.value === 'other' && radio.checked) {
                purposeOtherDetails.style.display = 'block';
            } else {
                purposeOtherDetails.style.display = 'none';
            }
        });
    });

    // Setting Type Radios (Step 3)
    settingTypeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            if (radio.value === 'auto' && radio.checked) {
                detailedSettingsDiv.style.display = 'none';
                autoSettingInfo.style.display = 'block';
            } else {
                detailedSettingsDiv.style.display = 'block';
                autoSettingInfo.style.display = 'none';
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

    // Generate Persona Button (Step 4)
    generatePersonaButton.addEventListener('click', async () => {
        // 1. Collect Form Data
        const formData = getFormData();
        formData.selected_tab = currentTab; // Include the selected tab

        console.log("Collected form data:", formData);

        // Basic validation before sending (add more as needed)
        if (!formData.department) { 
             alert('Step 1: 診療科が選択されていません。');
             showStep(1);
             return;
        }
         if (!formData.purpose) {
             alert('Step 2: 目的が選択されていません。');
             showStep(2);
             return;
        }

        // 2. Show Loading Step
        showStep(5);
        mainContainer.classList.remove('result-active'); // Ensure normal layout during loading
        resultProfileContainer.style.display = 'none';
        previewArea.style.display = 'none'; // Hide preview during loading

        // 3. Send data to backend
        try {
            // Use the correct URL for the Flask backend
            const apiUrl = 'http://127.0.0.1:5000/api/generate'; 
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log("Received result:", result);

            // THE ASSIGNMENT
            currentPersonaResult = result;
            console.log("Assigned to currentPersonaResult:", currentPersonaResult);

            // 4. Populate and Show Results
            populateResults(result);
            showStep(6);
            mainContainer.classList.add('result-active'); // Apply result layout
            previewArea.style.display = 'flex'; // Show preview area again
            resultProfileContainer.style.display = 'block'; // Show profile in preview

        } catch (error) {
            console.error('Error generating persona:', error);
            alert('ペルソナの生成中にエラーが発生しました。');
            // Revert to the previous step (e.g., Step 4)
            showStep(4);
            previewArea.style.display = 'flex'; // Show preview area again if it was hidden
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
        document.getElementById('preview-persona-image').src = result.profile?.image_url || ''; // Handle missing image
        document.getElementById('preview-name').textContent = result.profile?.name || '-';
        document.getElementById('preview-location').textContent = result.profile?.location || '-';
        // Separate Gender and Age population
        document.getElementById('preview-gender').textContent = result.profile?.gender || '-';
        document.getElementById('preview-age').textContent = result.profile?.age || '-'; 
        // Remove combined population: document.getElementById('preview-gender-age').textContent = `${result.profile?.gender || '-'} | ${result.profile?.age || '-'}`;
        document.getElementById('preview-occupation').textContent = result.profile?.occupation || '-';
        document.getElementById('preview-income').textContent = result.profile?.income || '-';
        document.getElementById('preview-hobby').textContent = result.profile?.hobby || '-';
        // Add handling for additional fields if displayed in preview
    }

    // --- Initial Setup --- 
    showStep(1); // Show the first step initially

    // Initialize state for step 2 & 3 options
    if (purposeOtherDetails) purposeOtherDetails.style.display = 'none';
    if (autoSettingInfo) autoSettingInfo.style.display = 'none';
    if (detailedSettingsDiv) detailedSettingsDiv.style.display = 'block'; // Show detailed settings by default

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
                const response = await fetch('http://127.0.0.1:5000/api/download/pdf', { // Use absolute URL
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
                const response = await fetch('http://127.0.0.1:5000/api/download/ppt', { // Target the new PPT endpoint
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
            // Optionally hide all if settings are missing
            if (pdfBtn) pdfBtn.style.display = 'none';
            if (pptBtn) pptBtn.style.display = 'none';
            if (gslideBtn) gslideBtn.style.display = 'none';
            return;
        }

        if (pdfBtn) pdfBtn.style.display = settings.pdf ? 'inline-block' : 'none';
        if (pptBtn) pptBtn.style.display = settings.ppt ? 'inline-block' : 'none';
        if (gslideBtn) gslideBtn.style.display = settings.gslide ? 'inline-block' : 'none';
    }

}); 