CXX := g++
CXXFLAGS := -O3 -march=native
all: mcsp

mcsp: main.cpp graph.cpp graph.h
	$(CXX) $(CXXFLAGS) -Wall -std=c++11 -o mcspDAL graph.cpp main.cpp -pthread
