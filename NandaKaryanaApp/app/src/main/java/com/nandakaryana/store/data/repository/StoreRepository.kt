package com.nandakaryana.store.data.repository

import com.nandakaryana.store.data.model.*
import com.nandakaryana.store.data.remote.StoreApiService
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class StoreRepository @Inject constructor(
    private val api: StoreApiService
) {
    private val cart = mutableListOf<CartItem>()

    fun getProducts(): Flow<Result<List<Product>>> = flow {
        try {
            emit(Result.Loading)
            val response = api.getProducts()
            if (response.success) {
                emit(Result.Success(response.data ?: emptyList()))
            } else {
                emit(Result.Error(response.message))
            }
        } catch (e: Exception) {
            emit(Result.Error(e.message ?: "Unknown error occurred"))
        }
    }

    fun getCategories(): Flow<Result<List<Category>>> = flow {
        try {
            emit(Result.Loading)
            val categories = listOf(
                Category(1, "Pulses", "seedling"),
                Category(2, "Snacks & Chips", "cookie"),
                Category(3, "Stationery", "pencil-alt"),
                Category(4, "Crockery", "utensils"),
                Category(5, "Bathroom Items", "shower"),
                Category(6, "Groceries", "bread-slice"),
                Category(7, "Household", "pump-soap"),
                Category(8, "Fresh Produce", "apple-alt")
            )
            emit(Result.Success(categories))
        } catch (e: Exception) {
            emit(Result.Error(e.message ?: "Unknown error occurred"))
        }
    }

    fun getCart(): Flow<Result<List<CartItem>>> = flow {
        emit(Result.Success(cart.toList()))
    }

    fun addToCart(product: Product): Flow<Result<List<CartItem>>> = flow {
        try {
            val existingItem = cart.find { it.product.id == product.id }
            if (existingItem != null) {
                existingItem.quantity++
            } else {
                cart.add(CartItem(product))
            }
            emit(Result.Success(cart.toList()))
        } catch (e: Exception) {
            emit(Result.Error(e.message ?: "Failed to add item to cart"))
        }
    }

    fun removeFromCart(productId: Int): Flow<Result<List<CartItem>>> = flow {
        try {
            cart.removeAll { it.product.id == productId }
            emit(Result.Success(cart.toList()))
        } catch (e: Exception) {
            emit(Result.Error(e.message ?: "Failed to remove item from cart"))
        }
    }

    fun checkout(): Flow<Result<Order>> = flow {
        try {
            emit(Result.Loading)
            val response = api.checkout(cart.toList())
            if (response.success) {
                cart.clear()
                emit(Result.Success(response.data!!))
            } else {
                emit(Result.Error(response.message))
            }
        } catch (e: Exception) {
            emit(Result.Error(e.message ?: "Checkout failed"))
        }
    }
}
