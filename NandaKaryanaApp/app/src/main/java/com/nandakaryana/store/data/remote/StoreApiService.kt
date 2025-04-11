package com.nandakaryana.store.data.remote

import com.nandakaryana.store.data.model.*
import retrofit2.http.*

interface StoreApiService {
    @GET("products")
    suspend fun getProducts(): ApiResponse<List<Product>>

    @GET("products/{id}")
    suspend fun getProduct(@Path("id") id: Int): ApiResponse<Product>

    @GET("cart")
    suspend fun getCart(): ApiResponse<List<CartItem>>

    @POST("cart")
    suspend fun addToCart(@Body item: CartItem): ApiResponse<List<CartItem>>

    @DELETE("cart/{productId}")
    suspend fun removeFromCart(@Path("productId") productId: Int): ApiResponse<List<CartItem>>

    @POST("checkout")
    suspend fun checkout(@Body items: List<CartItem>): ApiResponse<Order>
}

object ApiConstants {
    const val BASE_URL = "http://10.0.2.2:5000/api/" // Android emulator localhost
}

// Network Module for Dependency Injection
package com.nandakaryana.store.di

import com.nandakaryana.store.data.remote.ApiConstants
import com.nandakaryana.store.data.remote.StoreApiService
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(ApiConstants.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideStoreApiService(retrofit: Retrofit): StoreApiService {
        return retrofit.create(StoreApiService::class.java)
    }
}
