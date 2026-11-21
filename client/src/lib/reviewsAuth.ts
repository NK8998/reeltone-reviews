export const reviewsCookie = "reeltone_reviews";
export const reviewsApi = "/api/reeltone";

export type ReviewsUser = {
  id: string;
  username: string;
  firstName: string | null;
  lastName: string | null;
  imageUrl: string | null;
};
