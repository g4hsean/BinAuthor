#include <Windows.h>
#include <TlHelp32.h>
#include <iostream>
#include <stdio.h>
#include <tchar.h>
#include <psapi.h>
using namespace std;

BOOL CALLBACK EnumWindowsProc(_In_ HWND hwnd, _In_ LPARAM lParam)
{

	DWORD currentProId;
	::GetWindowThreadProcessId(hwnd, &currentProId);
	
	if (currentProId == lParam)
	{
		::SendMessage(hwnd, WM_SETTINGCHANGE, 0, (LPARAM)L"Environment");
		//return false;
	}
	return true;
}

void PrintProcessNameAndID(DWORD processID)
{
	TCHAR szProcessName[MAX_PATH] = TEXT("<unknown>");

	// Get a handle to the process.

	HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION |
		PROCESS_VM_READ,
		FALSE, processID);

	// Get the process name.

	if (NULL != hProcess)
	{
		HMODULE hMod;
		DWORD cbNeeded;

		if (EnumProcessModules(hProcess, &hMod, sizeof(hMod),
			&cbNeeded))
		{
			GetModuleBaseName(hProcess, hMod, szProcessName,
				sizeof(szProcessName) / sizeof(TCHAR));
		}
	}

	// Print the process name and identifier.
	if (!_tcscmp(_wcslwr(szProcessName), _T("explorer.exe")))
	{
		_tprintf(TEXT("%s  (PID: %u)\n"), _wcslwr(szProcessName), processID);
		DWORD procID = ::GetProcessId(hProcess);
		::EnumWindows(EnumWindowsProc, procID);
	}
	// Release the handle to the process.

	CloseHandle(hProcess);
}

int main()
{
	
	// Get the list of process identifiers.

	DWORD aProcesses[1024], cbNeeded, cProcesses;
	unsigned int i;

	if (!EnumProcesses(aProcesses, sizeof(aProcesses), &cbNeeded))
	{
		return 1;
	}


	// Calculate how many process identifiers were returned.

	cProcesses = cbNeeded / sizeof(DWORD);

	// Print the name and process identifier for each process.

	for (i = 0; i < cProcesses; i++)
	{
		if (aProcesses[i] != 0)
		{
			PrintProcessNameAndID(aProcesses[i]);
		}
	}
	
	cout << "System environment path variable set successfully!";
	return 0;
}


