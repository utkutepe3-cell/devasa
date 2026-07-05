APP=tsys-terminal
SRC=tsys_terminal.cpp
CXX?=g++
CXXFLAGS?=-std=c++17 -O2 -Wall -Wextra -pedantic

.PHONY: all run clean

all: $(APP)

$(APP): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(APP)

run: $(APP)
	./$(APP)

clean:
	rm -f $(APP)
