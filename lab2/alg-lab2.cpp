#include <iostream>
#include <cmath>
using namespace std;

void base()
{
    double hour;
    cout << "Введите количество часов" << "\n";
    cin >> hour;
    if (cin.fail() || hour<0)
    {
        cout << "Неверный тип данных, введите положительное число" << "\n";
        cin.clear();
        cin.ignore(10000,'\n');
        return;
    }
    int minutes{static_cast<int>(hour*60)};
    cout << "Количество минут = " << minutes << "\n";
}

void medium()
{
    double pi{3.1415};
    double R,h;
    cout << "Введите радиус и высоту" << "\n";
    cin >> R >> h;
    if (cin.fail() || h<=0 || R<=0)
    {
        cout << "Неверный тип данных, введите положительные числа" << "\n";
        cin.clear();
        cin.ignore(10000,'\n');
        return;
    }
    double V{pi*static_cast<double>(R*R)*h};
    cout << "Объем цилиндра = " << V << "\n";
}

void advanced()
{
    double x;
    int y;
    cout << "Введите числа x и y" << "\n";
    cin >> x >> y;
    if (cin.fail())
    {
        cin.clear();
        cin.ignore(10000,'\n');
        cout << "Неверный тип данных, введите числа";
        return;
    }
    double result{pow(x,static_cast<double>(y))};
    cout << "Результат: " << result << "\n";
}

int main(){
    int task_level;
    cout << "Выберите уровень задания" << "\n" << "1 - базовый" << "\n" << "2 - средний" << "\n" << "3 - повышенный" << "\n";
    cin >> task_level;
    if (cin.fail())
    {
        cout << "Неверный тип данных";
        cin.clear();
        cin.ignore(10000,'\n');
        //return;
    }
    if (task_level==1)
    {
        base();
    }
    else if (task_level == 2)
    {
        medium();
    }
    else if (task_level == 3)
    {
        advanced();
    }
    else
    {
        cout << "Неверный ввод, введите 1 или 2 или 3" << "\n";
    }
    return 0;
}