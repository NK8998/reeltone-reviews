import axios, { type AxiosInstance } from "axios";
import { reviewsApi } from "@/lib/reviewsAuth";
import type {
  Film, FilmData, FilmPageReview, FilmsPageData, FilteredFilms,
  LandingDataType, MembersPage, mePageTypes, RecentReviews, SearchResults,
} from "@/types/types";

type ReviewResult<T> = { message: string; film_data: T };
type ReviewEdit = Partial<Pick<FilmPageReview, "id" | "user_id" | "review_text" | "rating" | "updated_at">>;
export type ActivityResult = { message: { message: string } };
type FilmActivity = { film_id: number; film_title: string; film_poster: string };

export function createBackendService(http: AxiosInstance) {
  return {
    async landingData() {
      return (await http.get<LandingDataType>("/landing/all")).data;
    },
    async meData() {
      return (await http.get<mePageTypes>("/me/all")).data;
    },
    async filmsData() {
      return (await http.get<FilmsPageData>("/films/all")).data;
    },
    async filmData(query: string) {
      return (await http.get<FilmData>("/film/all", { params: { query } })).data;
    },
    async addToWatchList(film: FilmActivity) {
      return (await http.post<{ message: { message: string; is_in_watchlist: boolean } }>("/film/watchlist", film)).data;
    },
    async addToFavourites(film_id: string) {
      return (await http.post<ActivityResult>("/film/like", { film_id })).data;
    },
    async addToWatched(film: FilmActivity) {
      return (await http.post<ActivityResult>("/film/watched", film)).data;
    },
    async addReview(review: {
      film_id: number; review_text: string; rating?: number; film_title?: string; film_poster?: string;
    }) {
      return (await http.post<ReviewResult<FilmPageReview>>("/film/reviews/add", review)).data;
    },
    async editReview(review_id: number, new_content: string, rating: number) {
      return (await http.post<ReviewResult<ReviewEdit>>("/film/reviews/edit", { review_id, new_content, rating })).data;
    },
    async getFilteredFilms(searchParams: string) {
      return (await http.get<FilteredFilms>("/films/filter?" + searchParams)).data;
    },
    async getMembersPageData() {
      return (await http.get<MembersPage>("/members/all")).data;
    },
    async followMember(followed_id: string) {
      return (await http.post<{ message: string }>("/members/follows/add", { followed_id })).data;
    },
    async getMovieReviews(film_id: number) {
      return (await http.get<{ reviews: RecentReviews }>("/landing/films/reviews", { params: { film_id } })).data.reviews;
    },
    async getRelatedFilms(filmId: number) {
      return (await http.get<{ related_films: Film[] }>("/film/related", { params: { film_id: filmId } })).data;
    },
    async searchByTitle(title: string, page: number) {
      return (await http.get<SearchResults>(`/search/title/${encodeURIComponent(title)}`, { params: { page } })).data;
    },
  };
}

export const backendService = createBackendService(axios.create({ baseURL: reviewsApi }));
