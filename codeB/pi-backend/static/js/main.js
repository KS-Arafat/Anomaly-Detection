async function fetchWeather() {
	try {
		const response = await fetch("/sensor");
		if (!response.ok) throw new Error("Network response was not ok");

		const data = await response.json();

		// Update DOM
		document.getElementById(
			"city"
		).textContent = `${data.city}, ${data.country}`;
		document.getElementById("date").textContent = data.date;
		document.getElementById(
			"temp"
		).innerHTML = `${data.temperature}<span>°c</span>`;
		document.getElementById("weather").textContent = data.weather;
		document.getElementById(
			"hi-low"
		).textContent = `${data.temp_min}°c / ${data.temp_max}°c`;
	} catch (error) {
		console.error("Failed to fetch weather data:", error);
	}
}

// Fetch data on page load
window.addEventListener("DOMContentLoaded", fetchWeather);

function dateBuilder(d) {
	let months = [
		"January",
		"February",
		"March",
		"April",
		"May",
		"June",
		"July",
		"August",
		"September",
		"October",
		"November",
		"December",
	];
	let days = [
		"Sunday",
		"Monday",
		"Tuesday",
		"Wednesday",
		"Thursday",
		"Friday",
		"Saturday",
	];

	let day = days[d.getDay()];
	let date = d.getDate();
	let month = months[d.getMonth()];
	let year = d.getFullYear();

	return `${day} ${date} ${month} ${year}`;
}
