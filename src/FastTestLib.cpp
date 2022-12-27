// FastTestLib.cpp : Defines the exported functions for the DLL.
//

#ifdef _WIN32
#include "pch.h"
#endif 
#include "framework.h"
#include "FastTestLib.h"


// This is an example of an exported variable
FASTTESTLIB_API int nFastTestLib=0;

// This is an example of an exported function.
FASTTESTLIB_API int fnFastTestLib(void)
{
    return 0;
}

// This is the constructor of a class that has been exported.
CFastTestLib::CFastTestLib()
{
    return;
}
