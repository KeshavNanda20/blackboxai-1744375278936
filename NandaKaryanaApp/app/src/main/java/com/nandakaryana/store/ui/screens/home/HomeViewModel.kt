package com.nandakaryana.store.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nandakaryana.store.data.model.Category
import com.nandakaryana.store.data.model.Product
import com.nandakaryana.store.data.model.Result
import com.nandakaryana.store.data.repository.StoreRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val products: List<Product> = emptyList(),
    val filteredProducts: List<Product> = emptyList(),
    val categories: List<Category> = emptyList(),
    val selectedCategory: Category? = null,
    val searchQuery: String = "",
    val cartItemCount: Int = 0
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: StoreRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadInitialData()
    }

    private fun loadInitialData() {
        viewModelScope.launch {
            // Load categories
            repository.getCategories().collect { result ->
                when (result) {
                    is Result.Success -> {
                        _uiState.update { state ->
                            state.copy(categories = result.data)
                        }
                    }
                    is Result.Error -> {
                        _uiState.update { state ->
                            state.copy(error = result.message)
                        }
                    }
                    is Result.Loading -> {
                        _uiState.update { state ->
                            state.copy(isLoading = true)
                        }
                    }
                }
            }

            // Load products
            repository.getProducts().collect { result ->
                when (result) {
                    is Result.Success -> {
                        _uiState.update { state ->
                            state.copy(
                                isLoading = false,
                                products = result.data,
                                filteredProducts = result.data
                            )
                        }
                    }
                    is Result.Error -> {
                        _uiState.update { state ->
                            state.copy(
                                isLoading = false,
                                error = result.message
                            )
                        }
                    }
                    is Result.Loading -> {
                        _uiState.update { state ->
                            state.copy(isLoading = true)
                        }
                    }
                }
            }

            // Load cart count
            repository.getCart().collect { result ->
                when (result) {
                    is Result.Success -> {
                        _uiState.update { state ->
                            state.copy(cartItemCount = result.data.size)
                        }
                    }
                    else -> {} // Handle other cases if needed
                }
            }
        }
    }

    fun onSearchQueryChange(query: String) {
        _uiState.update { state ->
            state.copy(
                searchQuery = query,
                filteredProducts = filterProducts(state.products, query, state.selectedCategory)
            )
        }
    }

    fun onCategorySelected(category: Category?) {
        _uiState.update { state ->
            state.copy(
                selectedCategory = category,
                filteredProducts = filterProducts(state.products, state.searchQuery, category)
            )
        }
    }

    private fun filterProducts(
        products: List<Product>,
        query: String,
        category: Category?
    ): List<Product> {
        return products.filter { product ->
            val matchesQuery = product.name.contains(query, ignoreCase = true)
            val matchesCategory = category?.let { product.category == it.name } ?: true
            matchesQuery && matchesCategory
        }
    }

    fun addToCart(product: Product) {
        viewModelScope.launch {
            repository.addToCart(product).collect { result ->
                when (result) {
                    is Result.Success -> {
                        _uiState.update { state ->
                            state.copy(cartItemCount = result.data.size)
                        }
                    }
                    is Result.Error -> {
                        _uiState.update { state ->
                            state.copy(error = result.message)
                        }
                    }
                    else -> {} // Handle loading if needed
                }
            }
        }
    }
}
