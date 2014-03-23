
#include <stdio.h>

int g_a;
int g_arr[2] = {1, 2};
int* g_p;

typedef struct B
{
	int a;
} B;

struct A
{
	B b;
	int a;
};

struct A a;

int hoge() { return 0; }

int main(int argc, char* argv[])
{
	int hoge;
	for (int i=0; i<5; ++i) {
		if (i == 2) {
			hoge = 10;
		}
	}
	return 0;
	for (int i=0; i<5; ++i) {
		for (int j=0; j<5; ++j) {
			if (i == 3) {
				break;
			}
			{
				continue;
			}
			++i;
		}
		printf("%d\n", i);
	}
	return 0;
}

