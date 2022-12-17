// The following ifdef block is the standard way of creating macros which make exporting
// from a DLL simpler. All files within this DLL are compiled with the FASTTESTLIB_EXPORTS
// symbol defined on the command line. This symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see
// FASTTESTLIB_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
#ifdef FASTTESTLIB_EXPORTS
#define FASTTESTLIB_API __declspec(dllexport)
#else
#define FASTTESTLIB_API __declspec(dllimport)
#endif

// This class is exported from the dll
class FASTTESTLIB_API CFastTestLib {
public:
	CFastTestLib(void);
	// TODO: add your methods here.
};

extern FASTTESTLIB_API int nFastTestLib;

FASTTESTLIB_API int fnFastTestLib(void);
