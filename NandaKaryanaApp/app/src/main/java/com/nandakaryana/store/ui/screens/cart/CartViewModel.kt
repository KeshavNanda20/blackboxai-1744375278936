package com.nandakaryana.store.ui.screens.cart

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nandakaryana.store.data.model.CartItem
import com.nandakaryana.store.data.model.Result
import com.nandakaryana.store.data.repository.StoreRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class CartUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val cartItems: List<CartItem> = emptyList(),
    val subtotal: Double = 0.0,
    val total: Double = 0.0,
    val checkoutSuccess: Boolean = false
)

@HiltViewModel
class CartViewModel @Inject constructor(
    private val repository: StoreRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CartUiState())
    val uiState: StateFlow<CartUiState> = _uiState.asStateFlow()

    init {
        loadCart()
    }

    private fun loadCart() {
        viewModelScope.launch {
            repository.getCart().collect { result ->
                when (result) {
                    is Result.Success -> {
                        val cartItems = result.data
                        val subtotal = cartItems.sumOf { it.product.price * it.quantity }
                        _uiState.update { state ->
                            state.copy(
                                isLoading = false,
                                cartItems = cartItems,
                                subtotal = subtotal,
                                total = subtotal + 40 // Adding delivery charge
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
        }
    }

    fun removeFromCart(productId: Int) {
        viewModelScope.launch {
            repository.removeFromCart(productId).collect { result ->
                when (result) {
                    is Result.Success -> {
                        val cartItems = result.data
                        val subtotal = cartItems.sumOf { it.product.price * it.quantity }
                        _uiState.update { state ->
                            state.copy(
                                cartItems = cartItems,
                                subtotal = subtotal,
                                total = subtotal + 40
                            )
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

    fun checkout() {
        viewModelScope.launch {
            repository.checkout().collect { result ->
                when (result) {
                    is Result.Success -> {
                        _uiState.update { state ->
                            state.copy(
                                checkoutSuccess = true,
                                cartItems = emptyList(),
                                subtotal = 0.0,
                                total = 0.0
                            )
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
        }
    }
}
