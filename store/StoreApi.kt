package com.nandakaryana.store

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class StoreApi(private val baseUrl: String) {

    private val client = OkHttpClient()

    suspend fun getProducts(category: String? = null): String = withContext(Dispatchers.IO) {
        val url = if (category != null) {
            "$baseUrl/products/?category=$category"
        } else {
            "$baseUrl/products/"
        }
        val request = Request.Builder()
            .url(url)
            .get()
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Unexpected code $response")
            response.body?.string() ?: ""
        }
    }

    suspend fun getRecommendedProducts(productId: Int): String = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("$baseUrl/recommended-products/?product_id=$productId")
            .get()
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Unexpected code $response")
            response.body?.string() ?: ""
        }
    }

    suspend fun getCart(): String = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("$baseUrl/cart/")
            .get()
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Unexpected code $response")
            response.body?.string() ?: ""
        }
    }

    suspend fun addToCart(productId: Int, quantity: Int = 1): String = withContext(Dispatchers.IO) {
        val json = JSONObject()
        json.put("product_id", productId)
        json.put("quantity", quantity)
        val body = json.toString().toRequestBody("application/json".toMediaTypeOrNull())
        val request = Request.Builder()
            .url("$baseUrl/cart/add_item/")
            .post(body)
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Unexpected code $response")
            response.body?.string() ?: ""
        }
    }

    suspend fun checkout(deliveryAddress: String): String = withContext(Dispatchers.IO) {
        val json = JSONObject()
        json.put("delivery_address", deliveryAddress)
        val body = json.toString().toRequestBody("application/json".toMediaTypeOrNull())
        val request = Request.Builder()
            .url("$baseUrl/orders/checkout/")
            .post(body)
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Unexpected code $response")
            response.body?.string() ?: ""
        }
    }

    suspend fun acceptOrder(orderId: Int): String = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("$baseUrl/orders/$orderId/accept_order/")
            .post("".toRequestBody("application/json".toMediaTypeOrNull()))
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Unexpected code $response")
            response.body?.string() ?: ""
        }
    }

    suspend fun getOrderTracking(orderId: Int): String = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("$baseUrl/orders/$orderId/tracking/")
            .get()
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Unexpected code $response")
            response.body?.string() ?: ""
        }
    }

    suspend fun rateOrder(orderId: Int, rating: Int): String = withContext(Dispatchers.IO) {
        val json = JSONObject()
        json.put("rating", rating)
        val body = json.toString().toRequestBody("application/json".toMediaTypeOrNull())
        val request = Request.Builder()
            .url("$baseUrl/orders/$orderId/rate/")
            .post(body)
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("Unexpected code $response")
            response.body?.string() ?: ""
        }
    }
}
