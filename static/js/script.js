//blog writing
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#contentForm");
    const outputDiv = document.querySelector("#generatedContent");

    if (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            outputDiv.innerHTML = "<p>⏳ Generating AI Content, Please Wait...</p>";

            const contentType = document.querySelector("#content_type").value;
            const topic = document.querySelector("#topic").value;
            const length = document.querySelector("#length").value || "300"; 

            const requestData = {
                content_type: contentType,
                topic: topic,
                length: length
            };

            try {
                const response = await fetch("/generate-content", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(requestData)
                });

                const data = await response.json();

                if (data.generated_content) {
                    // Convert Newlines to <br> and Bold Formatting for Better Display
                    let formattedContent = data.generated_content
                        .replace(/\n/g, "<br>")  // Convert Newlines to HTML Line Breaks
                        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");  // Convert **Bold** to <strong>

                    outputDiv.innerHTML = `
                        <h3>Generated ${contentType.charAt(0).toUpperCase() + contentType.slice(1)}</h3>
                        <p>${formattedContent}</p>`;
                } else {
                    outputDiv.innerHTML = "<p>❌ AI failed to generate content. Try again.</p>";
                }
            } catch (error) {
                outputDiv.innerHTML = "<p>❌ Error: Could not generate content.</p>";
                console.error("Error:", error);
            }
        });
    }
});
//website 

//website 
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("websiteGeneratorForm");
    const previewContainer = document.getElementById("generatedWebsite");
    const previewFrame = document.getElementById("websitePreview");
    const codeContainer = document.getElementById("generatedCode");
    const codeBlock = document.getElementById("codeBlock");
    const copyButton = document.getElementById("copyCodeButton");
    const loader = document.getElementById("loadingIndicator");
    const loadingMessage = document.getElementById("loadingMessage"); 

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const businessType = document.getElementById("businessType").value.trim();
        const features = document.getElementById("features").value.trim();

        if (!businessType || !features) {
            alert("⚠ Please enter both Business Type and Features.");
            return;
        }

        // Show loading message
        if (loadingMessage) {
            loadingMessage.innerHTML = "<p>⏳ Website is loading, please wait...</p>";
            loadingMessage.classList.remove("d-none");
        }

        // Show loader
        if (loader) loader.classList.remove("d-none");

        fetch("/generate-website", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ businessType: businessType, features: features })
        })
        .then(response => response.json())
        .then((data) => {
            // ✅ Ensure `data` is defined before using it
            if (!data) {
                throw new Error("No response from the server.");
            }

            // Hide loader
            if (loader) loader.classList.add("d-none");
            if (loadingMessage) loadingMessage.classList.add("d-none");

            if (data.error) {
                alert("❌ Error: " + data.error);
                return;
            }

            // Ensure valid HTML output
            if (!data.website_code || data.website_code.trim() === "") {
                alert("❌ Error: AI did not generate valid HTML.");
                return;
            }

            console.log("Generated HTML:", data.website_code);

            // Show the generated website preview
            if (previewContainer) previewContainer.classList.remove("d-none");
            if (previewFrame) previewFrame.srcdoc = data.website_code;

            // Show the generated HTML code
            if (codeContainer) codeContainer.classList.remove("d-none");
            if (codeBlock) codeBlock.textContent = data.website_code;
        })
        .catch(error => {
            if (loader) loader.classList.add("d-none");
            if (loadingMessage) {
                loadingMessage.innerHTML = "<p style='color:red;'>❌ Error: Something went wrong!</p>";
            }
            console.error("Fetch Error:", error);
            alert("⚠ Something went wrong! Check the browser console.");
        });
    });


    // Copy code to clipboard
    if (copyButton) {
        copyButton.addEventListener("click", function () {
            navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                alert("✅ Code copied to clipboard!");
            }).catch(err => {
                console.error("Copy failed", err);
            });
        });
    }
});

// AI optimzer
document.addEventListener("DOMContentLoaded", function () {
    const optimizeForm = document.getElementById("optimize-form");
    const codeInput = document.getElementById("code");
    const optimizedOutput = document.getElementById("optimized-output");
    const loadingMessage = document.getElementById("loadingMessage");

    if (!optimizeForm || !loadingMessage || !optimizedOutput) {
        console.error("⚠️ Error: Missing elements for Code Optimizer!");
        return;
    }

    // Ensure loading message is hidden initially
    loadingMessage.style.display = "none";
    loadingMessage.classList.add("hidden");

    optimizeForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const code = codeInput.value.trim();
        if (!code) {
            alert("⚠ Please enter some code to optimize.");
            return;
        }

        // ✅ Show the loading message
        loadingMessage.innerHTML = "⏳ Optimizing Code, Please Wait...";
        loadingMessage.classList.remove("hidden");
        loadingMessage.style.display = "block";
        console.log("🔄 Showing loading message...");

        try {
            const response = await fetch("/optimize-code", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code: code })
            });

            const data = await response.json();

            // ✅ Hide the loading message after receiving a response
            loadingMessage.classList.add("hidden");
            loadingMessage.style.display = "none";
            console.log("✅ Hiding loading message...");

            if (data.error) {
                alert("❌ Error: " + data.error);
                return;
            }

            // ✅ Display the optimized code
            optimizedOutput.innerHTML = `<pre>${data.optimized_code}</pre>`;

        } catch (error) {
            // ✅ Hide the loading message on error
            loadingMessage.classList.add("hidden");
            loadingMessage.style.display = "none";
            console.error("❌ Fetch Error:", error);
            alert("⚠ Something went wrong! Check the browser console.");
        }
    });
});


//translation
function translateText() {
    let text = document.getElementById("inputText").value.trim();
    let lang = document.getElementById("language").value;

    if (!text) {
        alert("Please enter text to translate.");
        return;
    }

    fetch("/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dest_lang: lang, text: text })  // ✅ Correct key names
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            document.getElementById("outputText").innerText = data.translated_text || "Translation failed.";
        }
    })
    .catch(error => console.error("Error:", error));
}
//email generator
document.addEventListener("DOMContentLoaded", function () {
    const emailForm = document.getElementById("emailForm");

    if (!emailForm) {
        console.error("❌ Error: emailForm not found! Check if the form exists in dashboard.html.");
        return;
    }

    emailForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const emailType = document.getElementById("email_type").value;
        const details = document.getElementById("details").value;
        const emailOutput = document.getElementById("generatedEmail");

        emailOutput.innerHTML = "⏳ Generating email... Please wait.";

        try {
            const response = await fetch("/generate-email", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email_type: emailType, details: details }),
            });

            const data = await response.json();
            console.log("📩 API Response:", data); // Debugging log

            if (data && data.subject && data.email) {
                // ✅ Replace line breaks (\n) with <br> for correct HTML display
                const formattedEmail = data.email.replace(/\n/g, "<br>");

                emailOutput.innerHTML = `
                    <div style="padding: 15px; background-color: #222; color: #fff; border-radius: 5px; white-space: normal; line-height: 1.6;">
                        <p><strong style="color: yellow;">Subject:</strong> ${data.subject || "No Subject Provided"}</p>
                        <p><strong style="color: yellow;">Body:</strong></p>
                        <p>${formattedEmail}</p>  
                    </div>
                `;
            } else {
                console.error("❌ API Error: Missing subject or body in response", data);
                emailOutput.innerHTML = "❌ Error: Email generation failed. The API response is incomplete.";
            }
        } catch (error) {
            emailOutput.innerHTML = "❌ Error: Something went wrong.";
            console.error("⚠️ Fetch Error:", error);
        }
    });
});
//proofreading
function proofreadText() {
    let inputText = document.getElementById("proofreadingInput").value;
    
    if (!inputText) {
        alert("Please enter some text for proofreading.");
        return;
    }

    fetch("http://127.0.0.1:5000/proofread", {  // Change the URL if needed
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("proofreadingOutput").innerText = data.corrected_text;
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Failed to proofread text. Try again later.");
    });
}
//story writing
function generateStory() {
    const theme = document.getElementById("story-theme").value;
    const genre = document.getElementById("story-genre").value;
    const length = document.getElementById("story-length").value;
    const outputDiv = document.getElementById("story-output");

    // Validate input
    if (!theme) {
        outputDiv.innerHTML = "<p style='color: red;'>❌ Please enter a story theme!</p>";
        return;
    }

    outputDiv.innerHTML = "<p>⏳ Generating your story... Please wait.</p>";

    // API Request
    fetch("http://127.0.0.1:5000/generate-story", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme, genre, length }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.story) {
            outputDiv.innerHTML = `<h2 style="text-align: center;">Generated Story</h2><p>${data.story}</p>`;
        } else {
            outputDiv.innerHTML = "<p style='color: red;'>❌ Error: AI could not generate the story.</p>";
        }
    })
    .catch(error => {
        outputDiv.innerHTML = "<p style='color: red;'>❌ Error connecting to the AI server.</p>";
    });
}
//Mobile marketing
function generateMarketingMessage() {
    const campaignType = document.getElementById("campaign-type").value;
    const productDetails = document.getElementById("product-details").value;
    const outputDiv = document.getElementById("marketing-output");

    if (!productDetails) {
        outputDiv.innerHTML = "<p style='color: red;'>❌ Please enter product/service details!</p>";
        return;
    }

    outputDiv.innerHTML = "<p>⏳ Generating your marketing message... Please wait.</p>";

    fetch("http://127.0.0.1:5000/generate-marketing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ campaign_type: campaignType, product_details: productDetails }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.marketing_message) {
            outputDiv.innerHTML = `<h3>Generated Marketing Message:</h3><p>${data.marketing_message}</p>`;
        } else {
            outputDiv.innerHTML = "<p style='color: red;'>❌ Error: AI could not generate the message.</p>";
        }
    })
    .catch(error => {
        outputDiv.innerHTML = "<p style='color: red;'>❌ Error connecting to the AI server.</p>";
    });
}           
//SEO
document.addEventListener("DOMContentLoaded", function () {
    const seoButton = document.querySelector("#seoButton");
    const outputDiv = document.querySelector(".result");

    if (seoButton) {
        seoButton.addEventListener("click", async function () {
            const contentInput = document.querySelector("#contentInput").value;

            if (!contentInput.trim()) {
                alert("Please enter content for SEO optimization.");
                return;
            }

            // Show "Generating... Please Wait"
            seoButton.innerText = "Generating... Please Wait";
            seoButton.disabled = true;
            outputDiv.innerHTML = "<p>⏳ Generating SEO Optimization... Please Wait...</p>";

            try {
                const response = await fetch("/seo-optimize", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ content: contentInput })
                });

                const data = await response.json();

                if (data.error) {
                    outputDiv.innerHTML = `<p style="color: red;">❌ Error: ${data.error}</p>`;
                } else {

                    outputDiv.innerHTML = `
    <div style="background: #f4f4f4; padding: 15px; border-radius: 8px; color: #333;">
        <h3 style="color: #008000;">✅ Optimized Content:</h3>
        <p style="line-height: 1.6; font-size: 16px; font-weight: normal;">
            ${data.optimized_content.replace(/\n/g, "<br>")}
        </p>

        <h3 style="color: #333;">🔹 Suggested Keywords:</h3>
        <p style="font-weight: bold; color: #007bff; font-size: 16px;">
            ${data.keywords.join(", ")}
        </p>

        <h3 style="color: #333;">🔹 Generated Meta Description:</h3>
        <p style="font-style: italic; font-size: 16px;">
            "${data.meta_description}"
        </p>
    </div>`;
                }
            } catch (error) {
                outputDiv.innerHTML = "<p style='color: red;'>❌ Error: Could not generate SEO content.</p>";
                console.error("Error:", error);
            }

            // Reset button after completion
            seoButton.innerText = "Optimize SEO";
            seoButton.disabled = false;
        });
    }
});
//script writing
function generateYouTubeScript() {
    const topic = document.getElementById("youtube-topic").value.trim();
    const targetAudience = document.getElementById("youtube-audience").value.trim();
    const videoLength = parseInt(document.getElementById("youtube-length").value.trim()); // Convert to integer
    const outputDiv = document.getElementById("youtube-script-output");

    if (!topic || !targetAudience || !videoLength) {
        outputDiv.innerHTML = "<p style='color: red;'>❌ Please fill in all fields!</p>";
        return;
    }

    outputDiv.innerHTML = "<p>⏳ Generating YouTube script... Please wait.</p>";

    fetch("/generate-youtube-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, target_audience: targetAudience, video_length: videoLength }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.script) {
            let totalVideoDuration = videoLength * 60; // Convert minutes to seconds
            let scriptLines = data.script.split("\n");
            let sectionDuration = Math.floor(totalVideoDuration / scriptLines.length); // Calculate time per section
            let timeCounter = 0;

            let formattedScript = scriptLines
                .map(line => {
                    let minutes = Math.floor(timeCounter / 60).toString().padStart(2, '0');
                    let seconds = (timeCounter % 60).toString().padStart(2, '0');
                    let time = `[${minutes}:${seconds}]`;
                    timeCounter += sectionDuration; // Dynamically adjust time for each section
                    
                    // Adding Universal SEO Optimization Section
                    if (line.toLowerCase().includes("seo") || line.toLowerCase().includes("optimization")) {
                        line += "\n\n🔹 **Trending Keywords:** [Your topic-related trending keywords here]."
                    }
                    
                    // Adding Final Summary before CTA for Universal Topics
                    if (line.toLowerCase().includes("conclusion & cta") || line.toLowerCase().includes("final thoughts")) {
                        line = "🔹 **Key Takeaways:**\n1️⃣ [Key takeaway 1 based on topic].\n2️⃣ [Key takeaway 2 based on topic].\n3️⃣ [Key takeaway 3 based on topic].\n\n" + line;
                    }
                    
                    return `<p><strong style='color: #1E90FF;'>${time}</strong> ${line}</p>`;
                })
                .join("");

            outputDiv.innerHTML = `
                <h3>🎬 Generated YouTube Script:</h3>
                <div class="script-content">${formattedScript}</div>
            `;
        } else {
            outputDiv.innerHTML = "<p style='color: red;'>❌ Error: AI could not generate the script.</p>";
        }
    })
    .catch(error => {
        outputDiv.innerHTML = "<p style='color: red;'>❌ Error connecting to the AI server.</p>";
        console.error("Error:", error);
    });
}

//resume writing
async function generateResume() {
    const name = document.getElementById("name").value.trim();
    const jobTitle = document.getElementById("job_title").value.trim();
    const experience = document.getElementById("experience").value.trim();
    const skills = document.getElementById("skills").value.trim();
    const education = document.getElementById("education").value.trim();
    const startDate = document.getElementById("start_date").value.trim();
    const endDate = document.getElementById("end_date").value.trim();
    const resumeOutput = document.getElementById("resumeOutput");
    const downloadBtn = document.getElementById("downloadBtn");

    if (!name || !jobTitle) {
        resumeOutput.innerHTML = "<p style='color:red;'>❌ Name and job title are required.</p>";
        return;
    }

    resumeOutput.innerHTML = "⏳ Generating Resume... Please wait.";

    const response = await fetch("/generate-resume", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, job_title: jobTitle, experience, skills, education, start_date: startDate, end_date: endDate }),
    });

    const data = await response.json();
    if (data.resume && data.cover_letter) {
        resumeOutput.innerHTML = `<h3>Generated Resume:</h3>
                                  <pre>${data.resume}</pre>
                                  <h3>Generated Cover Letter:</h3>
                                  <pre>${data.cover_letter}</pre>`;
        downloadBtn.style.display = "block";

        // Store data for PDF download
        sessionStorage.setItem("resume", data.resume);
        sessionStorage.setItem("cover_letter", data.cover_letter);
    } else {
        resumeOutput.innerHTML = `<p style="color: red;">❌ Error: ${data.error}</p>`;
    }
}

async function downloadResume() {
    const resume = sessionStorage.getItem("resume");
    const coverLetter = sessionStorage.getItem("cover_letter");

    const response = await fetch("/download-resume", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume, cover_letter: coverLetter }),
    });

    const blob = await response.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "AI_Resume.pdf";
    link.click();
}
//bussines planning
document.addEventListener("DOMContentLoaded", function () {
    const pressForm = document.getElementById("pressReleaseForm");

    pressForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        // Get user input
        const pressType = document.getElementById("pressType").value;
        const headline = document.getElementById("headline").value;
        const keyDetails = document.getElementById("keyDetails").value;
        const contactInfo = document.getElementById("contactInfo").value;

        const requestData = { pressType, headline, keyDetails, contactInfo };

        // Show loading message
        document.getElementById("pressReleaseContent").innerHTML = "⏳ Generating Press Release... Please Wait...";

        try {
            const response = await fetch("/generate-press-release", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.press_release) {
                document.getElementById("generatedPressRelease").classList.remove("hidden");
                document.getElementById("pressReleaseContent").innerHTML = data.press_release.replace(/\n/g, "<br>");
            } else {
                document.getElementById("pressReleaseContent").innerHTML = "❌ Error: AI could not generate the press release.";
            }
        } catch (error) {
            document.getElementById("pressReleaseContent").innerHTML = "❌ Error: Something went wrong.";
            console.error("Error:", error);
        }
    });
});



//edit mode
document.addEventListener("DOMContentLoaded", function () {
    fetchOriginalContent();
});

// Fetch AI-generated content when a user selects a content type
function fetchOriginalContent() {
    const selectedModel = document.getElementById("contentType").value;

    fetch(`/get_original_content?model=${selectedModel}`)
        .then(response => response.json())
        .then(data => {
            if (data.original_content) {
                document.getElementById("aiGeneratedContent").value = data.original_content;
            } else {
                document.getElementById("aiGeneratedContent").value = "No original content found.";
            }
        })
        .catch(error => console.error("Error fetching original content:", error));
}

document.addEventListener("DOMContentLoaded", function () {
    const applyChangesButton = document.getElementById("applyChanges");
    const editedContentArea = document.getElementById("editedContent");
    const finalContentDiv = document.getElementById("finalContent");

    if (applyChangesButton) {
        applyChangesButton.addEventListener("click", async function () {
            const editedContent = editedContentArea.value.trim();

            if (!editedContent) {
                alert("Please enter some modifications before applying changes.");
                return;
            }

            finalContentDiv.innerHTML = "⏳ Processing your edits with AI... Please wait.";

            try {
                const response = await fetch("/edit-content", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ edited_content: editedContent }),
                });

                const data = await response.json();

                if (data.improved_content) {
                    finalContentDiv.innerHTML = `<p>${data.improved_content}</p>`;
                } else {
                    finalContentDiv.innerHTML = "<p>❌ AI could not process your edits. Try again.</p>";
                }
            } catch (error) {
                console.error("Error:", error);
                finalContentDiv.innerHTML = "<p>❌ Error connecting to AI server.</p>";
            }
        });
    }
});
// feed back 
document.addEventListener("DOMContentLoaded", function () {
    const feedbackSections = document.querySelectorAll(".feedback-section");

    feedbackSections.forEach(section => {
        const thumbsUpButton = section.querySelector(".thumbsUp");
        const thumbsDownButton = section.querySelector(".thumbsDown");
        const feedbackOptions = section.querySelector(".feedbackOptions");
        const customFeedback = section.querySelector(".customFeedback");
        const submitButton = section.querySelector(".submitFeedback");

        let feedbackType = "";

        thumbsUpButton.addEventListener("click", function () {
            feedbackType = "thumbs_up";
            thumbsUpButton.classList.add("bg-green-700");
            thumbsDownButton.classList.remove("bg-red-700");
        });

        thumbsDownButton.addEventListener("click", function () {
            feedbackType = "thumbs_down";
            thumbsDownButton.classList.add("bg-red-700");
            thumbsUpButton.classList.remove("bg-green-700");
        });

        submitButton.addEventListener("click", function () {
            const generatorName = section.getAttribute("data-generator"); // Get AI generator name
            const improvementSuggestion = feedbackOptions.value;
            const userFeedback = customFeedback.value.trim();

            if (!feedbackType) {
                alert("Please select 👍 or 👎 before submitting feedback!");
                return;
            }

            const feedbackData = {
                generator_name: generatorName,
                feedback_type: feedbackType,
                improvement_suggestion: improvementSuggestion,
                custom_feedback: userFeedback
            };

            fetch("/submit-feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(feedbackData)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                feedbackOptions.value = "more_creative"; // Reset dropdown
                customFeedback.value = ""; // Clear custom feedback
            })
            .catch(error => {
                console.error("Error submitting feedback:", error);
            });
        });
    });
});
// feedback anyalze
document.querySelectorAll(".improveWithAI").forEach(button => {
    button.addEventListener("click", async function () {
        const generatorName = this.getAttribute("data-generator");

        try {
            const response = await fetch("/analyze-feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ generator_name: generatorName })
            });

            const data = await response.json();
            if (data.improved_content) {
                alert(`✅ AI has generated an improved version for ${generatorName}!`);
                document.getElementById(`output-${generatorName}`).innerText = data.improved_content;
            } else {
                alert("❌ AI could not improve the content.");
            }
        } catch (error) {
            console.error("Error analyzing feedback:", error);
        }
    });
});
//improve
document.addEventListener("DOMContentLoaded", function () {
    const feedbackForm = document.getElementById("feedbackForm");
    const feedbackList = document.getElementById("feedbackList");

    // Function to submit feedback
    feedbackForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const generator = document.getElementById("generator").value;
        const originalContent = document.getElementById("originalContent").value;
        const improvement = document.getElementById("improvement").value;

        const response = await fetch("/submit_feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ generator, original_content: originalContent, improvement }),
        });

        const result = await response.json();
        if (result.success) {
            alert("Feedback submitted successfully!");
            fetchFeedback(); // Reload feedback list
        } else {
            alert("Error submitting feedback.");
        }
    });

    // Function to fetch feedback list
    async function fetchFeedback() {
        const response = await fetch("/get_feedback");
        const feedbacks = await response.json();

        feedbackList.innerHTML = ""; // Clear previous list

        feedbacks.forEach((feedback) => {
            const item = document.createElement("li");
            item.innerHTML = `
                <strong>${feedback.generator} Output:</strong><br>
                <em>Original:</em> ${feedback.original_content} <br>
                <em>Requested Improvement:</em> ${feedback.improvement} <br>
                <button onclick="improveContent(${feedback.id})">Improve</button>
                <div id="improvedContent-${feedback.id}"></div>
            `;
            feedbackList.appendChild(item);
        });
    }

    // Function to improve AI-generated content using Gemini
    async function improveContent(feedbackId) {
        const response = await fetch("/improve_ai_content", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ feedback_id: feedbackId }),
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById(`improvedContent-${feedbackId}`).innerHTML = `
                <strong>Improved Content:</strong><br> ${result.improved_content}
            `;
        } else {
            alert("Error improving content.");
        }
    }

    // Load feedback list on page load
    fetchFeedback();
});


