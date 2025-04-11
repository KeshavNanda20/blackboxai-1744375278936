package com.nandakaryana.store.data.model

data class Product(
    val id: Int,
    val name: String,
    val price: Double,
    val quantity: String,
    val image: String,
    val category: String,
    val description: String = ""
)

data class CartItem(
    val product: Product,
    var quantity: Int = 1
)

data class Category(
    val id: Int,
    val name: String,
    val icon: String
)

data class Order(
    val id: Int,
    val items: List<CartItem>,
    val total: Double,
    val date: String,
    val status: String
)

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

data class ApiResponse<T>(
    val success: Boolean,
    val message: String,
    val data: T?
)
