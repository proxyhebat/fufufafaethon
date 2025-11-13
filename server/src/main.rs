use axum::{Json, Router, response::IntoResponse, routing::post};
use serde::{Deserialize, Serialize};
use tokio::process::Command;

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct GeneratePayload {
    video_url: String,
    categories: Vec<Category>,
    user_prompt: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
enum Category {
    Podcast,
    Lifestyle,
    Vlog,
    Travel,
    FoodCooking,
    BeautyFashion,
    Fitness,
    Sports,
    Basketball,
    Soccer,
    AmericanFootball,
    MarketingWebinar,
    TalkingHeadSpeech,
    MotivationalSpeech,
    Commentary,
    Interview,
    Entertainment,
    Movies,
    DramaShows,
    RealityTalkShows,
    News,
    InformativeEducational,
    ProductReviews,
    History,
    ScienceTech,
    Music,
    Gaming,
    Other,
    Custom(String),
}

impl std::fmt::Display for Category {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Category::Podcast => write!(f, "Podcast"),
            Category::Lifestyle => write!(f, "Lifestyle"),
            Category::Vlog => write!(f, "Vlog"),
            Category::Travel => write!(f, "Travel"),
            Category::FoodCooking => write!(f, "Food & Cooking"),
            Category::BeautyFashion => write!(f, "Beauty & Fashion"),
            Category::Fitness => write!(f, "Fitness"),
            Category::Sports => write!(f, "Sports"),
            Category::Basketball => write!(f, "Basketball"),
            Category::Soccer => write!(f, "Soccer"),
            Category::AmericanFootball => write!(f, "American Football"),
            Category::MarketingWebinar => write!(f, "Marketing & Webinar"),
            Category::TalkingHeadSpeech => write!(f, "Talking Head & Speech"),
            Category::MotivationalSpeech => write!(f, "Motivational Speech"),
            Category::Commentary => write!(f, "Commentary"),
            Category::Interview => write!(f, "Interview"),
            Category::Entertainment => write!(f, "Entertainment"),
            Category::Movies => write!(f, "Movies"),
            Category::DramaShows => write!(f, "Drama Shows"),
            Category::RealityTalkShows => write!(f, "Reality & Talk Shows"),
            Category::News => write!(f, "News"),
            Category::InformativeEducational => write!(f, "Informative & Educational"),
            Category::ProductReviews => write!(f, "Product Reviews"),
            Category::History => write!(f, "History"),
            Category::ScienceTech => write!(f, "Science & Tech"),
            Category::Music => write!(f, "Music"),
            Category::Gaming => write!(f, "Gaming"),
            Category::Other => write!(f, "Other"),
            Category::Custom(s) => write!(f, "{}", s),
        }
    }
}

async fn generate_handler(Json(payload): Json<GeneratePayload>) -> impl IntoResponse {
    let job_id = "some_random_id";

    tokio::spawn(async move {
        let mut cmd = Command::new("python");
        cmd.arg("run");
        cmd.arg("fufufafa.py");
        cmd.arg(format!(
            "--with-category {}",
            payload
                .categories
                .iter()
                .map(|x| x.to_string())
                .collect::<Vec<String>>()
                .join(", ")
        ));
        if let Some(prompt) = payload.user_prompt {
            cmd.arg(format!("--prompt {}", prompt));
        }

        let exit_status = cmd
            .spawn()
            .expect("Failed to start")
            .wait()
            .await
            .expect("Failed to run");

        println!("TODO: handle the exit status {}", exit_status);
    });

    Json(serde_json::json!(
        {
            "data": {
                "jobId": job_id
            }
        }
    ))
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let app = Router::new().route("/generate", post(generate_handler));
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await?;
    axum::serve(listener, app).await?;
    Ok(())
}
