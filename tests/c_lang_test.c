/*
 * Test program for DDD 
 */
#include <stdio.h>
#include <string.h>
#define DAYSINWEEK 7
 
int test(int a){
	a = 123123;
	return a+123;
}	

void test2(){
	int a = 1;
	int b= 1;
	a = a +b;
}
 struct structTest {
		int a;
		int b;
		int c;
};
	
void main()
{
	//Declarations
    int ndays, year, week, days;
	double doubleA, doubleB;
	float floatA;
	char a[10];
	
 
	//Attribuition 
	int a1=1;
	int b,c;
	b = 23;
	doubleA = 1.2312;
	doubleB = 3.4212;
	floatA = 23.2;
	a[0] = 'a';
	a[1] = 0x0;
	
	//Operator
	a1++;    //Bug - Space issue
	a1+=1;   //Bug - Space issue
	a1--;    //Bug - Space issue
	a1+=b;   //Bug - Space issue
	a1 -= 1;
	b = a1 * b + ( a1 /1)+ (b % 2);  //Bug - Max number of variables changed is low
	
	//Struct
	struct structTest structTestVar;
	struct structTest structTestVar2;
	structTestVar = structTestVar2;
	
	structTestVar.a = 10;
	structTestVar2.a = structTestVar.a;  //Bug - Struct issue
	
	//String
	char strtest[10] = "abcdefghi";
	char *pstr = strcpy(strtest,"testtt");   //Bug - Space issue strcpy(strtest
	pstr = strcpy( strtest ,"testtt22");
	
    ndays = 13144;
    year = ndays / 365;
    week =(ndays % 365) / DAYSINWEEK;
    days =(ndays % 365) % DAYSINWEEK;
    printf ("%d is equivalent to %d years, %d weeks and %d daysn",ndays, year, week, days);
	int a3 = 10;
	week =  test(a3);
	week++;
	test2();
	return;
}