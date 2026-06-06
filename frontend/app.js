async function generatePRD() {
  // Step 1: Get the values the user typed
  const productName = document.getElementById("productName").value.trim();
  const productDescription = document.getElementById("productDescription").value.trim();
 
  // Step 2: Validate both fields are filled
  if (!productName || !productDescription) {
    alert("Please fill in both fields!");
    return;
  }
 
  // Step 3: Show loading state
  const btn = document.getElementById("generateBtn");
  const output = document.getElementById("outputContent");
  const tag = document.getElementById("outputTag");
 
  btn.disabled = true;
  btn.querySelector(".btn-text").innerHTML = `<span class="dots">Generating</span>`;
 
  output.className = "output-content";
  output.textContent = "Calling backend API, please wait...";
  tag.textContent = "Generating...";
  tag.className = "output-tag loading";
 
  // Step 4: Call the backend API using fetch()
  try {
    const response = await fetch("http://127.0.0.1:8000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_name: productName,
        product_description: productDescription
      })
    });
 
    // Step 5: Parse the JSON response
    const data = await response.json();
 
    // Step 6: Display the response on screen
    output.textContent = JSON.stringify(data, null, 2);
    output.classList.add("has-data");
    tag.textContent = "✓ Ready";
    tag.className = "output-tag ready";
 
  } catch (error) {
    // Step 7: If something goes wrong, show the error
    output.textContent = "⚠ Error: Could not connect to the backend.\n\nMake sure uvicorn is running:\n  cd ai-pm-assistant\n  uvicorn main:app --reload";
    output.className = "output-content";
    tag.textContent = "Error";
    tag.className = "output-tag error";
    console.error(error);
 
  } finally {
    // Step 8: Always re-enable the button
    btn.disabled = false;
    btn.querySelector(".btn-text").innerHTML = `<span class="btn-icon">✦</span> Generate PRD`;
  }
}
 
  