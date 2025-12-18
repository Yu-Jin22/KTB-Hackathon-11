import axios from "axios";


export interface Ingredient {
    name: string;
    amount: string;
    unit: string;
    note: string;
}

export interface RecipeResultPayload {
    title: string;
    description: string;
    servings: string;
    totalTime: string;
    difficulty: string;
    ingredients: Ingredient[];
    steps: RecipeStep[];
    tips: string[];
}

export interface RecipeStep {
    stepNumber: number;
    instruction: string;
    timestamp: number;
    duration: string;
    details: string;
    tips: string;
    imageUrl: string;
}
const api = axios.create({
    baseURL: "/spring-api",
});

// 레시피 저장
export const saveRecipe = async (recipeData: RecipeResultPayload): Promise<any> => {
    const response = await api.post('/recipe', recipeData);
    return response.data;
}

// 레시피 재료 저장
export const saveIngredient = async (ingredientData: Ingredient): Promise<any> => {
    const response = await api.post('/ingredient', ingredientData);
    return response.data;
}

// 레시피 과정 저장
export const saveRecipeStep = async (stepData: RecipeStep): Promise<any> => {
    const response = await api.post('/recipe-step', stepData);
    return response.data;
}

// 레시피 불러오기
export const fetchRecipes = async (): Promise<RecipeResultPayload> => {
    const response = await api.get('/recipes');
    return response.data;
}

export default api;
