<script setup lang="ts">
import { ref, onMounted } from 'vue'

// reactive state
const count = ref(0)

// functions that mutate state and trigger updates
function increment() {
  count.value++
}

// lifecycle hooks
onMounted(async () => {
  console.log(`The initial count is ${count.value}.`)
  // This is where we request stats data
  // albums, num wanted, downloaded
  // songs, num wanted, downloaded, progress

  // Request artists data
})
</script>

<template>
  <div class="greetings">
    <h3>
      You’ve successfully created a project with
      <a href="https://vite.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>.
      What's next?
    </h3>

    <div>
      This will be the artist/song management page
        <form action="{% url 'library_manager:download_playlist' %}" method="post">
            <!-- {% csrf_token %} -->
            <!-- {{ playlist_form }} -->
            <input type="submit" name='download playlist' value="Download">
        </form>

        <div>
            <div>
                <!-- Albums: Num Wanted: {{ extra_stats.num_wanted }} | Num Downloaded: {{ extra_stats.num_downloaded }} -->
            </div>
            <div>
                <!-- Songs: Sum Num Wanted: {{ extra_stats.sum_num_wanted }} | Sum Num Downloaded: {{ extra_stats.sum_num_downloaded }} || Progress: {{ extra_stats.percent_completed}}% -->
            </div>
        </div>

        <div class="track_artist_row">
            <form action="{% url 'library_manager:fetch_all_for_tracked_artists' %}" method="post">
                <!-- {% csrf_token %} -->
                <input type="submit" name='fetch all missing albums for tracked artists' value="Fetch All">
            </form>

            <form action="{% url 'library_manager:download_all_for_tracked_artists' %}" method="post">
                <!-- {% csrf_token %} -->
                <input type="submit" name='download all missing albums for tracked artists' value="Download All Missing For Tracked Artists">
            </form>

            <form action="{% url 'library_manager:index' %}" method="get">
                <!-- {% csrf_token %} -->
                <input name="search_artist" type="text" placeholder="Search artists...">
                <input type="submit" name='search artists' value="Search">
            </form>
        </div>

        <!-- {% if page_obj %} -->
        <ul>
        <!-- {% for artist_details in page_obj %} -->
            <li>
                <div class="track_artist_row">
                    <!-- <a href="{% url 'library_manager:artist' artist_details.id %}">Tracked [{% if artist_details.tracked %}X{% else %}_{%endif%}] {{ artist_details.name }} - {{ artist_details.number_songs }} Song(s) | Albums: ({{ artist_details.albums.known }} Known |  {{ artist_details.albums.missing }} Missing)</a> -->
                    <form action="{% url 'library_manager:download_wanted_albums_for_artist' artist_details.id %}" method="post">
                        <!-- {% csrf_token %} -->
                        <input type="submit" name='download wanted albums for artist' value="Download Wanted Albums">
                    </form>
                </div>
            </li>
        <!-- {% endfor %} -->
        </ul>

        <!-- <div class="pagination"> -->
            <!-- <span class="step-links"> -->
                <!-- {% if page_obj.has_previous %} -->
                    <!-- <a href="{{ search_term_and_page }}=1">&laquo; first</a> -->
                    <!-- <a href="{{ search_term_and_page }}={{ page_obj.previous_page_number }}">previous</a> -->
                <!-- {% endif %} -->
        
                <!-- <span class="current"> -->
                    <!-- Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}. -->
                <!-- </span> -->
        
                <!-- {% if page_obj.has_next %} -->
                    <!-- <a href="{{ search_term_and_page }}={{ page_obj.next_page_number }}">next</a> -->
                    <!-- <a href="{{ search_term_and_page }}={{ page_obj.paginator.num_pages }}">last &raquo;</a> -->
                <!-- {% endif %} -->
            <!-- </span> -->
        <!-- </div> -->
        <!-- {% else %} -->
            <!-- <p>No artists are available.</p> -->
        <!-- {% endif %} -->
      </div>
    </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
