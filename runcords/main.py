import requests
import time
import os
simport json
import sys
import subprocess
from bs4 import BeautifulSoup

start_time = time.time()
total_files_saved = 0
total_bytes_saved = 0

DEPOTS = {
	"BP": ["Q51", "Q110", "Q1115", "Q112", "Q1134", "QM21"],
	"CA": ["MISC", "S4090", "S4252", "S4696", "S4898", "S5181", "S53", "S54", "S66", "S7686", "S93", "SIM3", "SIM30", "SIM32", "SIM33", "SIM34", "SIM35"],
	"CH": ["MISC", "S55", "S56", "S7484", "S78", "SIM2", "SIM4", "SIM8", "SIM10", "SIM23", "SIM24", "SIM25", "SIM26", "SIM31"],
	"CP": ["Q25", "Q26", "Q28", "Q63", "Q64", "Q65", "Q66", "Q74", "QM1", "QM2", "QM4", "QM5", "QM6", "QM7", "QM8", "QM10", "QM11", "QM12", "QM20", "QM31", "QM32", "QM35", "QM36", "QM40", "QM42", "QM44"],
	"CS": ["MISC", "Q12", "Q13", "Q15", "Q16", "Q20", "Q31", "Q38", "Q58", "Q61", "Q76", "Q90", "Q98", "SBS44"],
	"EC": ["BX23", "Q50", "BXM6", "BXM7", "BXM8", "BXM9", "BXM10"],
	"EN": ["B12", "B14", "B15", "B17", "B25", "B42", "B45", "B65", "B82", "B83", "B84", "Q24", "Q56", "SBS82"],
	"FB": ["B2", "B31", "B41", "B44", "B46", "B49", "SB44", "SBS46"],
	"FP": ["B7", "B13", "B20", "B26", "B47", "B52", "B54", "B60", "Q14", "Q54", "Q55"],
	"FR": ["Q11", "Q22", "Q35", "Q41", "QM15", "QM167", "QM18"],
	"GA": ["B24", "B32", "B38", "B39", "B48", "B57", "B62", "Q29", "Q39", "Q59", "Q67"],
	"GH": ["BX44A", "BX5", "BX12", "BX16", "BX22", "BX24", "BX29", "BX30", "BX34", "BX39", "BX41", "BX2838", "BX256", "BX402", "SBS12", "SBS41"],
	"JA": ["MISC", "Q3", "Q4", "Q5", "Q17", "Q30", "Q42", "Q77", "Q84", "Q85", "Q86", "Q87", "Q89"],
	"JG": ["B4", "B8", "B9", "B11", "B16", "B35", "B37", "B43", "B61", "B63", "B6769", "B68", "B70"],
	"JK": ["Q6", "Q7", "Q8", "Q9", "Q37", "Q40", "Q60", "Q1080", "SBS52", "QM65"],
	"KB": ["BX1", "BX2", "BX3", "BX7", "BX9", "BX10", "BX13", "BX15", "BX18", "BX20", "BX2838", "M100"],
	"LG": ["Q18", "Q19", "Q23", "Q32", "Q33", "Q47", "Q49", "Q69", "Q72", "Q100", "Q101", "Q102", "Q103", "Q104", "SBS53", "SBS70", "QM24", "QM25", "QM34"],
	"MQ": ["M8", "M9", "M12", "M20", "M21", "M22", "M42", "M50", "M55", "M57", "M66", "M72", "SB79", "SBS14", "SBS23", "SBS34", "SBS60", "SBS86"],
	"MV": ["M2", "M3", "M4", "M5", "M10", "M11", "M96", "M98", "M104", "M116"],
	"OF": ["M1", "M7", "M35", "M125", "SBS15"],
	"OH": ["M15", "M31", "M101"],
	"QV": ["MISC", "Q1", "Q2", "Q27", "Q36", "Q43", "Q45", "Q46", "Q48", "Q75", "Q82", "Q83", "Q88", "QM63", "QM64", "QM68"],
	"SC": ["B100", "B103", "BM1", "BM2", "BM3", "BM4", "BM5"],
	"UP": ["B1", "B3", "B6", "B36", "B64", "B74", "X2737", "X2838"],
	"WF": ["BX6", "BX8", "BX11", "BX17", "BX19", "BX21", "BX27", "BX31", "BX32", "BX33", "BX35", "BX36", "BX46", "SBS6"],
	"YO": ["YOAS", "BXM1", "BXM2", "BXM3", "BXM4", "BXM11", "BXM18"],
	"YU": ["MISC", "S4494", "S57", "S59", "S6191", "S6292", "S89", "SBS79", "SIM1", "SIM6", "SIM7", "SIM9", "SIM10", "SIM11", "SIM15", "SIM22"]
}

TIME_SPAN_ID = "ctl00_ContentPlaceHolder1_Label112"
PICK_SPAN_ID = "ctl00_ContentPlaceHolder1_lblPick"
SCHEDULE_SPAN_ID = "ctl00_ContentPlaceHolder1_Label13"

def main():
	global CONFIG_FILE, BASE_URL
	CONFIG_FILE = os.path.expanduser(".runcords_config.json")
	BASE_URL = get_base_url()

	process()

	end_time = time.time()
	duration = end_time - start_time

	print("\n===== SUMMARY =====")
	print(f"Total paddles saved: {total_files_saved}")
	print(f"Total size saved: {total_bytes_saved / 1024:.2f} KB")
	print(f"Total runtime: {duration:.2f} seconds")

def print_warning():
	RED = "\033[91m"
	YELLOW = "\033[93m"
	RESET = "\033[0m"

	print(
		f"{RED}WARNING: {RESET}"
		f"{YELLOW}The BASE URL to the BusTrek website is now saved LOCALLY in PLAIN text in this folder. Avoid sending anyone this folder directly and direct them to the GitHub repo."
		f"{RESET}"
	)

def get_base_url():
	if os.path.exists(CONFIG_FILE):
		with open(CONFIG_FILE, "r") as f:
			return json.load(f)["BASE_URL"]

	print_warning()
	
	response = input("Did you read the README, and do you understand the risks of using this program? Type I UNDERSTAND to continue: ").strip()

	if response != "I UNDERSTAND":
		print("Program terminated. Please read the README before using this tool.")
		sys.exit(1)

	base_url = input("Enter the passphrase: ").strip()

	if not base_url:
		print("No passphrase provided. Exiting.")
		sys.exit(1)

	with open(CONFIG_FILE, "w") as f:
		json.dump({"BASE_URL": base_url}, f)

	return base_url

def parse_page(html):
	soup = BeautifulSoup(html, "html.parser")
	
	time_span = soup.find("span", id=TIME_SPAN_ID)
	if not time_span or not time_span.text.strip():
		return None

	pick_span = soup.find("span", id=PICK_SPAN_ID)
	if not pick_span or not pick_span.text.strip():
		return None
	pick = pick_span.text.strip()

	schedule_span = soup.find("span", id=SCHEDULE_SPAN_ID)
	if not schedule_span or not schedule_span.text.strip():
		return None
	schedule_type = schedule_span.text.strip()

	return pick, schedule_type

def save_page(content, pick, depot, route, schedule_type, run):
	folder_path = os.path.join(pick, depot, route, schedule_type)
	os.makedirs(folder_path, exist_ok=True)

	file_path = os.path.join(folder_path, f"{run}.html")

	with open(file_path, "w", encoding="utf-8") as f:
		f.write(content)

	return os.path.getsize(file_path)

def process():
	global total_files_saved, total_bytes_saved

	for depot, routes in DEPOTS.items():
		for route in routes:
			for run in range(1000):
				input_value = f"{depot}_{route}_{run}"
				url = BASE_URL + input_value

				print(f"Checking {input_value}")

				try:
					response = requests.get(url, timeout=10)
				except requests.RequestException:
					continue

				if response.status_code != 200:
					continue

				result = parse_page(response.text)

				if result:
					pick, schedule_type = result
					size = save_page(response.text, pick, depot, route, schedule_type, run)
					
					total_files_saved += 1
					total_bytes_saved += size

					print(f"Saved {pick}/{depot}/{route}/{run}.html")

				time.sleep(0.5)

if __name__ == "__main__":
	main()	
