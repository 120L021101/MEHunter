#include <vector>
#include <set>
#include <string>

#include "NFA_c.h"

#define min(x, y) ( x <= y ? x : y )
#define max(x, y) ( x >= y ? x : y )
#define abs(x) (x >= 0 ? x : -x)

using namespace std;

void get_seed(const string& seq, int kmer, set<string>& seeds) {
    int start = 0, end = kmer;
    int str_length = seq.length();
    while (end <= str_length) {
        string&& sub_str = seq.substr( start, kmer );
        seeds.insert( sub_str );
        start ++;
        end ++;
    } return ;
}

float epsilon_NFA(const string& seq1, const string& seq2, float min_score = 0.7, int window_size = 2000) {
    int seq1_length = seq1.length(), seq2_length = seq2.length();
    window_size = int( seq2_length * (1 - min_score) ) + 1;
    int max_epochs = int( seq2_length * (2 - min_score) ) + 1;
    int epoch = 0;
    vector<int> states ( seq1_length + 1, -1 );
    states[0] = 0;

    while (epoch < max_epochs) {
        int s_idx_start = min(seq1_length, epoch);
        int s_idx_end = max(0, epoch - window_size);
        for (int s_idx = s_idx_start; s_idx >= s_idx_end; --s_idx) {
            if (s_idx == seq1_length) {
                states[s_idx]++;
                continue;
            }
            if (states[s_idx] < seq2_length && seq1[s_idx] == seq2[states[s_idx]]) {
                states[s_idx + 1] = max(
                    states[s_idx + 1],
                    states[s_idx] + 1
                );
            } else {
                states[s_idx + 1] = max(
                    states[s_idx + 1],
                    states[s_idx]
                );
            }
            states[s_idx] ++;
        }
        epoch ++;
        if (states[ seq1_length ] == seq2_length) break;
    }

    if (epoch == max_epochs) return 0;
    return max(
        0,
        min(
            1 - abs((float)epoch - seq2_length) / seq2_length,
            1 - abs((float)epoch - seq1_length) / seq1_length
        )
    );
}
float NFA_space::align_c( const string& input_s1, const string& input_s2, float min_score = 0.7 ) {
    int kmer = 6;
    set<string> seeds;
    const string& seq1 = input_s1.length() > input_s2.length() ? input_s1 : input_s2;
    const string& seq2 = input_s1.length() > input_s2.length() ? input_s2 : input_s1;

    int seq1_length = static_cast<int>(seq1.length());
    int seq2_length = static_cast<int>(seq2.length());

    if (seq2_length < 10) return 0.0f;

    int best_start = 0, start = 0, end = seq2_length, score = 0;
    
    // 冷启动
    int s = 0, e = kmer;
    while (e <= end) {
        string&& sd = seq1.substr( s, kmer );
        if ( seeds.count(sd) )
            score += 1;
        ++s; ++e;
    }
    int max_score = score;
    string &&s1 = seq1.substr(0, 10), &&s2 = seq2.substr(0, 10), &&s3 = seq1.substr(seq2_length - 10, 10), &&s4 = seq2.substr(seq2_length - 10, 10); 
    float ano_score = (
        epsilon_NFA(s1, s2) + epsilon_NFA(s3, s4)
    ) / 2;
    while (end < seq1_length) {
        ++end;
        string &&remove_kmer = seq1.substr(start, kmer);
        if (seeds.count(remove_kmer)) {
            score --;
        }
        string &&add_kmer = seq1.substr(end - kmer, kmer);
        if (seeds.count(add_kmer)) {
            score ++;
        }
        ++start;
        if (score > max_score) {
            string &&cur_seq = seq1.substr(start, seq2_length);
            string &&s1_ = cur_seq.substr(0, 10), &&s2_ = seq2.substr(0, 10), &&s3_ = cur_seq.substr(seq2_length - 10, 10), &&s4_ = seq2.substr(seq2_length - 10, 10);
            float a_score = (
                epsilon_NFA(s1_, s2_) + epsilon_NFA(s3_, s4_)
            ) / 2;
            if (a_score > ano_score) {
                max_score = score;
                best_start = start;
                ano_score = a_score;
            }
        }
    }
    const string &&s1_f = seq1.substr(best_start, seq2_length);
    const string &s2_f = seq2; 
    return epsilon_NFA(s1_f, s2_f, min_score);
}