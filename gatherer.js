    // Function to fetch JSON data from a file
    async function fetchData(url) {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    }

    // Function to populate the job table
    async function populateJobTable() {
        const jobTableBody = document.getElementById("jobTableBody");
        const dateFilter = document.getElementById("dateFilter");

        // Fetch data from data_gathered.json
        const jobData = await fetchData('data_gathered.json');

        // Track unique dates for the filter dropdown
        const uniqueDates = new Set();

        jobData.forEach(job => {
            const row = document.createElement("tr");
            const titleCell = document.createElement("td");
            const keywordCell = document.createElement("td"); // New cell for 'Keyword Found'
            const dateCell = document.createElement("td");
            const linkCell = document.createElement("td");

            titleCell.textContent = job.title;
            keywordCell.textContent = job.found_keywords.join(', '); // Populate 'Keyword Found'
            dateCell.textContent = job.date;

            const link = document.createElement("a");
            link.href = job.url;
            link.target = "_blank";
            link.textContent = "View Job";
            linkCell.appendChild(link);

            row.appendChild(titleCell);
            row.appendChild(keywordCell);
            row.appendChild(dateCell);
            row.appendChild(linkCell);

            jobTableBody.appendChild(row);

            // Collect unique dates
            uniqueDates.add(job.date);
        });

        // Clear existing options
        dateFilter.innerHTML = "";

        // Populate the date filter dropdown
        if (uniqueDates.size > 1) {
            const dateFilterOptions = document.createElement("option");
            dateFilterOptions.value = "all";
            dateFilterOptions.textContent = "No Filter";
            dateFilter.appendChild(dateFilterOptions);
        }

        uniqueDates.forEach(date => {
            const option = document.createElement("option");
            option.value = date;
            option.textContent = date;
            dateFilter.appendChild(option);
        });
    }

    // Call the function to populate the job table
    populateJobTable();

    // Function to filter jobs based on search input and date filter
    function filterJobs() {
        const searchInput = document.getElementById("searchInput").value.toLowerCase();
        const dateFilter = document.getElementById("dateFilter").value;
        const jobRows = document.querySelectorAll("#jobTableBody tr");

        jobRows.forEach(row => {
            const title = row.querySelector("td:first-child").textContent.toLowerCase();
            const date = row.querySelector("td:nth-child(2)").textContent;

            const titleMatch = title.includes(searchInput);
            const dateMatch = dateFilter === "all" || date === dateFilter;

            if (titleMatch && dateMatch) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    }