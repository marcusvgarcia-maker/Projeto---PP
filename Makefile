
CXX = g++
MPICXX = mpic++
CXXFLAGS = -O2 -std=c++17

BUILD = build

.PHONY: all baseline openmp perfilamento validacao mpi amdahl clean

# Implementacoes atualmente disponiveis
all: baseline openmp perfilamento validacao mpi amdahl

$(BUILD):
	mkdir -p $(BUILD)

# Baseline sequencial
baseline: $(BUILD)/10_kmeans_base

$(BUILD)/10_kmeans_base: sequencial/10_kmeans.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) $< -o $@

# OpenMP
openmp: $(BUILD)/10_kmeans_omp

$(BUILD)/10_kmeans_omp: openmp/10_kmeans.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) -fopenmp $< -o $@

# Perfilamento
perfilamento: $(BUILD)/10_kmeans_perfil

$(BUILD)/10_kmeans_perfil: perfilamento/10_kmeans.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) $< -o $@

# Programas de validacao
validacao: $(BUILD)/validacao_seq $(BUILD)/validacao_omp

$(BUILD)/validacao_seq: validacao/sequencial.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) $< -o $@

$(BUILD)/validacao_omp: validacao/openmp.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) -fopenmp $< -o $@

# MPI — implementacao disponivel
mpi: $(BUILD)/10_kmeans_mpi

$(BUILD)/10_kmeans_mpi: mpi/10_kmeans.cpp | $(BUILD)
	$(MPICXX) $(CXXFLAGS) $< -o $@

# Perfilamento adicional para o modelo de Amdahl
amdahl: $(BUILD)/10_kmeans_amdahl

$(BUILD)/10_kmeans_amdahl: perfilamento/10_kmeans_amdahl.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) $< -o $@

# Remover apenas os executaveis gerados
clean:
	rm -rf $(BUILD)
