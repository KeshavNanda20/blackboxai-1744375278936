package com.nandakaryana.store.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.nandakaryana.store.ui.screens.home.HomeScreen
import com.nandakaryana.store.ui.screens.cart.CartScreen
import com.nandakaryana.store.ui.screens.product.ProductDetailScreen

@Composable
fun NavGraph(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route
    ) {
        composable(route = Screen.Home.route) {
            HomeScreen(navController = navController)
        }
        composable(route = Screen.Cart.route) {
            CartScreen(navController = navController)
        }
        composable(
            route = Screen.ProductDetail.route + "/{productId}",
        ) {
            ProductDetailScreen(
                navController = navController,
                productId = it.arguments?.getString("productId") ?: ""
            )
        }
    }
}

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Cart : Screen("cart")
    object ProductDetail : Screen("product")
}
