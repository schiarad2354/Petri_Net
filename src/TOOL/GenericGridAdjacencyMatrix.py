class GenericGridAdjacencyMatrix:
    @staticmethod
    def rook_adjacency_matrix(number_of_patches):
        rook_adj_matrix = np.zeros((number_of_patches**2, number_of_patches**2), dtype=int)

        for i in range(number_of_patches):
            for j in range(number_of_patches):
                idx = i * number_of_patches + j
                if i > 0:
                    rook_adj_matrix[idx, idx - number_of_patches] = 1  # Up
                if i < number_of_patches - 1:
                    rook_adj_matrix[idx, idx + number_of_patches] = 1  # Down
                if j > 0:
                    rook_adj_matrix[idx, idx - 1] = 1  # Left
                if j < number_of_patches - 1:
                    rook_adj_matrix[idx, idx + 1] = 1  # Right

        return rook_adj_matrix

    @staticmethod
    def queen_adjacency_matrix(number_of_patches):
        queen_adj_matrix = np.zeros((number_of_patches**2, number_of_patches**2), dtype=int)

        for i in range(number_of_patches):
            for j in range(number_of_patches):
                idx = i * number_of_patches + j
                if i > 0:
                    queen_adj_matrix[idx, idx - number_of_patches] = 1  # Up
                if i < number_of_patches - 1:
                    queen_adj_matrix[idx, idx + number_of_patches] = 1  # Down
                if j > 0:
                    queen_adj_matrix[idx, idx - 1] = 1  # Left
                if j < number_of_patches - 1:
                    queen_adj_matrix[idx, idx + 1] = 1  # Right
                if i > 0 and j > 0:
                    queen_adj_matrix[idx, idx - number_of_patches - 1] = 1  # Up-Left
                if i > 0 and j < number_of_patches - 1:
                    queen_adj_matrix[idx, idx - number_of_patches + 1] = 1  # Up-Right
                if i < number_of_patches - 1 and j > 0:
                    queen_adj_matrix[idx, idx + number_of_patches - 1] = 1  # Down-Left
                if i < number_of_patches - 1 and j < number_of_patches - 1:
                    queen_adj_matrix[idx, idx + number_of_patches + 1] = 1  # Down-Right

        return queen_adj_matrix
