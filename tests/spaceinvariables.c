/*
 * Test program for DDD 
 */
#include <stdio.h>
#include <string.h>

void main()
{
	int a1=1;
	int b=2;
	a1++;    //Bug - Space issue
	a1+=1;   //Bug - Space issue
	a1--;    //Bug - Space issue
	a1+=b;   //Bug - Space issue
}